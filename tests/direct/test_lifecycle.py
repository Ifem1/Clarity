"""Installed genlayer-test Direct Mode: real SDK/storage, mocked web and LLM.

These tests execute public methods, but do not prove network consensus, transfer
delivery or atomic rollback. In particular run_validator does not undo leader
storage; disagreement rollback remains a live GenVM release gate.
"""
import datetime
import json
import pytest
from test_clarity_direct import deploy

AMOUNT = 10**17
START = 1792411200  # 2026-10-19T12:00:00Z


def warp(vm, seconds):
    timestamp=datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).isoformat()
    vm.warp(timestamp)
    # 0.29.2 warps datetime.now, but omits message_raw['datetime'] refresh.
    import sys
    if 'genlayer.gl' in sys.modules:
        sys.modules['genlayer.gl'].message_raw['datetime']=timestamp


@pytest.fixture
def setup(direct_vm, direct_deploy, direct_alice, direct_bob):
    vm = direct_vm
    warp(vm, START)
    alice=direct_alice
    bob=direct_bob
    vm.sender = alice
    c = deploy(direct_deploy)
    rows = [{'title':f'Task {n}', 'requirement':'The public record demonstrates completion',
             'recipient':'0x'+bytes(bob).hex(), 'allocation_bps':bps,
             'dependencies':[] if n == 0 else [0],
             'sources':[{'url':'https://alpha.example.org/record','role':'PRIMARY','required':True},
                        {'url':'https://beta.example.net/record','role':'CORROBORATING','required':True}],
             'challenge_sources':[]} for n,bps in enumerate([4000,6000])]
    return vm,c,rows,alice,bob


def fund(s, rows=None, value=AMOUNT):
    vm,c,base,alice,bob=s
    vm.value=value
    c.create_grant('Public evidence','Two milestones',START+86400,300,AMOUNT,json.dumps(base if rows is None else rows))
    vm.value=0
    return c


def mocks(vm, label='SATISFIED', body='The public record demonstrates completion.'):
    vm.clear_mocks()
    vm.mock_web('.*',{'status':200,'body':body})
    vm.mock_llm('.*',label)


def submit(s,n=0):
    vm,c,rows,alice,bob=s
    vm.sender=bob
    c.submit_task(1,n)


def provisional(s,n=0,label='SATISFIED'):
    submit(s,n)
    mocks(s[0],label)
    s[1].evaluate_task(1,n)


def conservation(c):
    a=c.get_accounting()
    assert a['funded']==a['remaining']+a['paid']+a['refunded']
    assert a['bonds_received']==a['bonds_locked']+a['bonds_returned']+a['bonds_forfeited']


def test_funded_creation(setup):
    c=fund(setup)
    assert c.get_grant(1).total==AMOUNT
    assert [c.get_task(1,n).amount for n in (0,1)]==[4*10**16,6*10**16]
    conservation(c)


def test_public_views_encode(setup):
    c=fund(setup)
    assert c.get_grant(1).total==AMOUNT
    assert c.get_task(1,0).amount==4*10**16
    assert c.get_accounting()['remaining']==AMOUNT
    assert c.get_status_names()[0]=='AWAITING'


def test_failed_native_transfer_does_not_change_genvm_ledgers(setup):
    """Direct Mode cannot execute/rollback child GEN transfers; pin this boundary."""
    c=fund(setup)
    provisional(setup,0)
    warp(setup[0],START+300)
    c.finalize_task(1,0)
    vm=setup[0]
    before=c.get_accounting().copy()
    with pytest.raises(RuntimeError,match='recipient rejected transfer'):
        vm._gl_call_hook=lambda _vm,request: (_ for _ in ()).throw(RuntimeError('recipient rejected transfer')) if 'EthSend' in request else None
        c.claim_task(1,0)
    # Python Direct Mode does not snapshot/rollback storage on an exception.
    # The attempted claim's write-first accounting persists here; chain semantics
    # need a real GenVM child-message failure test before release.
    after=c.get_accounting()
    assert after['paid']==before['paid']+4*10**16
    assert after['remaining']==before['remaining']-4*10**16


def test_unauthorized_submit(setup):
    c=fund(setup)
    with pytest.raises(AssertionError,match='only assigned contributor'):
        c.submit_task(1,0)


@pytest.mark.parametrize('value',[0,AMOUNT-1,AMOUNT+1])
def test_incorrect_funding(setup,value):
    with pytest.raises(AssertionError,match='exact native GEN'):
        fund(setup,value=value)
    assert setup[1].get_grant_count()==0


@pytest.mark.parametrize('dependencies',[[1],[-1],[0,0],[True]])
def test_invalid_graph(setup,dependencies):
    rows=setup[2]
    rows[0]['dependencies']=dependencies
    with pytest.raises(ValueError):
        fund(setup,rows)


def test_independent_validator_agreement_and_commitment(setup):
    c=fund(setup)
    provisional(setup)
    assert c.get_task(1,0).status==3
    assert setup[0].run_validator() is True
    assert setup[0].run_validator(leader_result='SATISFIED|'+'0'*64+'|'+'0'*64) is False
    mocks(setup[0],body='Changed bytes')
    assert setup[0].run_validator() is False
    conservation(c)


def test_dependency_activation_and_claim(setup):
    c=fund(setup)
    provisional(setup,1)
    warp(setup[0],START+300)
    c.finalize_task(1,1)
    assert c.get_task(1,1).status==5
    with pytest.raises(AssertionError,match='not claimable'):
        c.claim_task(1,1)
    provisional(setup,0)
    warp(setup[0],START+600)
    c.finalize_task(1,0)
    c.activate_task(1,1)
    c.claim_task(1,0)
    c.claim_task(1,1)
    assert c.get_accounting()['paid']==AMOUNT
    assert setup[0].transfers
    assert [(int(v),on) for _,v,on in setup[0].transfers[-2:]]==[(4*10**16,'finalized'),(6*10**16,'finalized')]
    received=[(a.as_bytes.hex(),v,on) for a,v,on in setup[0].transfers]
    assert received[-2:]==[(bytes(setup[4]).hex(),4*10**16,'finalized'),
                           (bytes(setup[4]).hex(),6*10**16,'finalized')]
    with pytest.raises(AssertionError,match='not claimable'):
        c.claim_task(1,0)
    conservation(c)


def test_violated_refund(setup):
    c=fund(setup)
    provisional(setup,label='VIOLATED')
    warp(setup[0],START+300)
    c.finalize_task(1,0)
    c.refund_task(1,0)
    assert c.get_accounting()['refunded']==4*10**16
    with pytest.raises(AssertionError,match='already settled'):
        c.refund_task(1,0)
    conservation(c)


@pytest.mark.parametrize('final,ledger',[('SATISFIED','bonds_returned'),('VIOLATED','bonds_forfeited')])
def test_bonded_challenge(setup,final,ledger):
    c=fund(setup)
    provisional(setup,label='VIOLATED')
    vm=setup[0]
    bond=2*10**15
    vm.value=bond
    c.challenge_task(1,0,'Recheck the authorized evidence')
    vm.value=0
    mocks(vm,final)
    c.resolve_challenge(1,0)
    assert vm.run_validator() is True
    assert c.get_accounting()[ledger]==bond
    assert c.get_accounting()['bonds_locked']==0
    assert setup[0].transfers[-1][1:]==(bond,'finalized')
    beneficiary=bytes(setup[4]).hex()
    assert setup[0].transfers[-1][0].as_bytes.hex()==(beneficiary if final=='SATISFIED' else bytes(setup[3]).hex())
    conservation(c)


def test_inconclusive_recovery_retry_and_refund(setup):
    c=fund(setup)
    provisional(setup,label='VIOLATED')
    vm=setup[0]
    vm.value=2*10**15
    c.challenge_task(1,0,'Evidence is ambiguous')
    vm.value=0
    mocks(vm,'INCONCLUSIVE')
    c.resolve_challenge(1,0)
    assert c.get_task(1,0).status==4
    warp(vm,START+86400)
    c.recover_stalled_challenge(1,0)
    assert c.get_accounting()['bonds_returned']==2*10**15
    assert setup[0].transfers[-1][1:]==(2*10**15,'finalized')
    c.evaluate_task(1,0)
    warp(vm,START+86460)
    c.evaluate_task(1,0)
    with pytest.raises(AssertionError,match='attempt limit'):
        c.evaluate_task(1,0)
    warp(vm,START+8*86400)
    c.refund_task(1,0)
    c.refund_task(1,1)
    assert c.get_accounting()['refunded']==AMOUNT
    assert [(v,on) for _,v,on in setup[0].transfers[-2:]]==[(4*10**16,'finalized'),(6*10**16,'finalized')]
    conservation(c)
