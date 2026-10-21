"""Installed genlayer-test Direct Mode: real SDK/storage, mocked web and LLM.

These tests execute public methods, but do not prove network consensus, transfer
delivery or atomic rollback. In particular run_validator does not undo leader
storage; disagreement rollback remains a live GenVM release gate.
"""
import datetime
import hashlib
import json
import pytest
from test_clarity_direct import deploy

AMOUNT = 10**17
MAX_SOURCE_TEXT = 2200
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
    c = deploy(direct_deploy)
    vm.sender = bob
    vm.origin = bob
    c.register_recipient()
    vm.sender = alice
    vm.origin = alice
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
    assert c.is_registered_recipient('0x'+bytes(setup[4]).hex()) is True
    conservation(c)


def test_contract_recipient_rejected_even_if_address_is_supplied(setup):
    vm,c,rows,alice,bob=setup
    rows[0]['recipient']='0x'+'c'*40
    vm.value=AMOUNT
    c.create_grant('Public evidence','Two milestones',START+86400,300,AMOUNT,json.dumps(rows))
    assert c.get_grant_count()==0
    assert c.get_funding_recovery(alice)==AMOUNT


def test_recipient_registration_rejects_contract_forwarding(setup):
    vm,c,rows,alice,bob=setup
    vm.sender=bob
    vm.origin=alice
    with pytest.raises(AssertionError,match='direct EOA transaction'):
        c.register_recipient()


def test_sponsor_grant_creation_rejects_contract_forwarding(setup):
    vm,c,rows,alice,bob=setup
    vm.sender=alice
    vm.origin=bob
    vm.value=AMOUNT
    c.create_grant('Public evidence','Two milestones',START+86400,300,AMOUNT,json.dumps(rows))
    assert c.get_grant_count()==0
    assert c.get_funding_recovery(bob)==AMOUNT
    vm.sender=bob
    vm.origin=bob
    c.recover_failed_funding()
    assert vm.transfers[-1][0].as_bytes==bytes(bob)


def test_unknown_payable_selector_credits_origin_recovery(setup):
    vm,c,_,alice,_=setup
    vm.value=12345
    c.__handle_undefined_method__('unknown_selector',[],{})
    assert c.get_grant_count()==0
    assert c.get_funding_recovery(alice)==12345
    vm.value=0


def test_failed_emitted_transfer_is_recoverable_only_by_recipient(setup):
    vm,c,_,alice,bob=setup
    fund(setup)
    provisional(setup,0)
    warp(vm,START+300)
    c.finalize_task(1,0)
    vm.sender=bob
    vm.origin=bob
    value=c.get_task(1,0).amount
    c.claim_task(1,0)
    assert vm.transfers[-1][0].as_bytes==bytes(bob)

    # Simulate GenVM's error callback: origin is preserved from the direct
    # recipient claim and the returned native value is exposed as message.value.
    vm.sender=alice
    vm.origin=bob
    vm.value=value
    c.__on_errored_message__()
    assert c.get_failed_transfer_recovery(bob)==value
    assert c.get_accounting()['failed_transfer_recovery']==value

    vm.sender=alice
    vm.origin=alice
    vm.value=0
    with pytest.raises(AssertionError,match='no failed transfer credit'):
        c.recover_failed_transfer()

    vm.sender=bob
    vm.origin=bob
    vm.value=0
    c.recover_failed_transfer()
    assert c.get_failed_transfer_recovery(bob)==0
    assert c.get_accounting()['failed_transfer_recovery']==0
    assert vm.transfers[-1][0].as_bytes==bytes(bob)
    assert vm.transfers[-1][2]=='finalized'


def test_public_views_encode(setup):
    c=fund(setup)
    assert c.get_grant(1).total==AMOUNT
    assert c.get_task(1,0).amount==4*10**16
    assert c.get_accounting()['remaining']==AMOUNT
    assert c.get_status_names()[0]=='AWAITING'


def test_direct_mode_child_send_exception_has_no_rollback_or_retry(setup):
    """Direct Mode cannot execute/rollback child GEN transfers; pin this boundary."""
    c=fund(setup)
    provisional(setup,0)
    warp(setup[0],START+300)
    c.finalize_task(1,0)
    vm=setup[0]
    vm.sender=setup[4]
    vm.origin=setup[4]
    before=c.get_accounting().copy()
    with pytest.raises(RuntimeError,match='recipient rejected transfer'):
        vm._gl_call_hook=lambda _vm,request: (_ for _ in ()).throw(RuntimeError('recipient rejected transfer')) if 'EthSend' in request else None
        c.claim_task(1,0)
    # Python Direct Mode does not snapshot/rollback storage on an exception.
    # Callback-based recovery is exercised separately because Direct Mode does
    # not execute asynchronous child messages.
    after=c.get_accounting()
    assert after['paid']==before['paid']+4*10**16
    assert after['remaining']==before['remaining']-4*10**16
    assert c.get_task(1,0).status==8
    with pytest.raises(AssertionError,match='not claimable'):
        c.claim_task(1,0)


def test_unauthorized_submit(setup):
    c=fund(setup)
    with pytest.raises(AssertionError,match='only assigned contributor'):
        c.submit_task(1,0)


@pytest.mark.parametrize('value',[0,AMOUNT-1,AMOUNT+1])
def test_incorrect_funding(setup,value):
    c=fund(setup,value=value)
    assert c.get_grant_count()==0
    owner=setup[3]
    assert c.get_funding_recovery(owner)==value
    if value:
        c.recover_failed_funding()
        assert c.get_funding_recovery(owner)==0
        assert setup[0].transfers[-1][1:]==(value,'finalized')


@pytest.mark.parametrize('dependencies',[[1],[-1],[0,0],[True]])
def test_invalid_graph(setup,dependencies):
    rows=setup[2]
    rows[0]['dependencies']=dependencies
    c=fund(setup,rows)
    assert c.get_grant_count()==0
    assert c.get_funding_recovery(setup[3])==AMOUNT


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
    setup[0].sender=setup[4]
    setup[0].origin=setup[4]
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


def test_ready_dependency_blocks_stale_blocked_refund(setup):
    c=fund(setup)
    provisional(setup,1)
    warp(setup[0],START+300)
    c.finalize_task(1,1)
    assert c.get_task(1,1).status==5
    provisional(setup,0)
    warp(setup[0],START+600)
    c.finalize_task(1,0)
    assert c.get_task(1,0).status==6
    warp(setup[0],START+9*86400)
    setup[0].sender=setup[3]
    setup[0].origin=setup[3]
    with pytest.raises(AssertionError,match='not refundable'):
        c.refund_task(1,1)
    c.activate_task(1,1)
    setup[0].sender=setup[4]
    setup[0].origin=setup[4]
    c.claim_task(1,1)
    assert c.get_task(1,1).status==8


def test_dependency_completion_after_refund_does_not_reopen_allocation(setup):
    c=fund(setup)
    submit(setup,0)
    mocks(setup[0],'SATISFIED')
    c.evaluate_task(1,0)
    provisional(setup,1)
    assert c.get_task(1,0).status==3
    warp(setup[0],START+300)
    c.finalize_task(1,1)
    assert c.get_task(1,1).status==5
    warp(setup[0],START+9*86400)
    setup[0].sender=setup[3]
    setup[0].origin=setup[3]
    c.refund_task(1,1)
    c.finalize_task(1,0)
    assert c.get_task(1,0).status==6
    assert c.get_task(1,1).status==9
    with pytest.raises(AssertionError,match='prerequisites not satisfied'):
        c.activate_task(1,1)


def test_sponsor_source_mutation_cannot_replace_provisional_evidence(setup):
    c=fund(setup)
    provisional(setup,0,'SATISFIED')
    manifest=c.get_manifest(1,0,'PRIMARY',1)
    frozen=json.loads(manifest.evidence_json)
    assert frozen[0]['text']=='The public record demonstrates completion.'
    vm=setup[0]
    vm.sender=setup[3]
    vm.value=2*10**15
    c.challenge_task(1,0,'The sponsor altered its publisher after the provisional review')
    vm.value=0
    # The live publisher now contradicts the task. Challenge review must use
    # the stored original primary bytes, not render the mutable URL again.
    mocks(vm,'SATISFIED','The record now contradicts completion.')
    c.resolve_challenge(1,0)
    assert c.get_task(1,0).status==6
    assert c.get_task(1,0).final_label=='SATISFIED'
    challenge=json.loads(c.get_manifest(1,0,'CHALLENGE',1).evidence_json)
    assert challenge[0]['text']=='The public record demonstrates completion.'


def test_unresolved_challenge_preserves_original_decision(setup):
    setup[2][0]['challenge_sources']=[{'url':'https://gamma.example.com/challenge','role':'CHALLENGE','required':True}]
    c=fund(setup)
    provisional(setup,0,'SATISFIED')
    vm=setup[0]
    vm.sender=setup[3]
    vm.value=2*10**15
    c.challenge_task(1,0,'Attempted evidence mutation')
    vm.value=0
    mocks(vm,'INCONCLUSIVE','')
    c.resolve_challenge(1,0)
    assert c.get_task(1,0).status==4
    warp(vm,START+86400)
    c.recover_stalled_challenge(1,0)
    assert c.get_task(1,0).status==6
    assert c.get_task(1,0).final_label=='SATISFIED'
    assert c.get_accounting()['bonds_returned']==2*10**15


def test_oversized_source_is_rejected_without_truncation(setup):
    c=fund(setup)
    submit(setup,0)
    full='A'*MAX_SOURCE_TEXT+' CONTRADICTION'
    mocks(setup[0],'SATISFIED',full)
    c.evaluate_task(1,0)
    assert c.get_task(1,0).status==2
    manifest=c.get_manifest(1,0,'PRIMARY',1)
    assert manifest.label=='SOURCE_TOO_LARGE'
    evidence=json.loads(manifest.evidence_json)
    assert evidence[0]['too_large'] is True
    assert evidence[0]['content_digest']==hashlib.sha256(full.encode()).hexdigest()


def test_digest_covers_mutation_beyond_old_truncation_boundary(setup):
    c=fund(setup)
    vm=setup[0]
    prefix='A'*MAX_SOURCE_TEXT
    mocks(vm,'SATISFIED',prefix+' original tail')
    first=c._review(c.get_task(1,0),False)
    mocks(vm,'SATISFIED',prefix+' changed tail')
    assert vm.run_validator(leader_result=first) is False


def test_violated_refund(setup):
    c=fund(setup)
    provisional(setup,label='VIOLATED')
    warp(setup[0],START+300)
    c.finalize_task(1,0)
    setup[0].sender=setup[3]
    setup[0].origin=setup[3]
    c.refund_task(1,0)
    assert c.get_accounting()['refunded']==4*10**16
    with pytest.raises(AssertionError,match='already settled'):
        c.refund_task(1,0)
    conservation(c)


@pytest.mark.parametrize('final,ledger',[('SATISFIED','bonds_returned'),('VIOLATED','bonds_forfeited')])
def test_bonded_challenge(setup,final,ledger):
    c=fund(setup)
    provisional(setup,label='SATISFIED')
    vm=setup[0]
    bond=2*10**15
    vm.sender=setup[3]
    vm.origin=setup[3]
    vm.value=bond
    c.challenge_task(1,0,'Recheck the authorized evidence')
    vm.value=0
    t=c._task(1,0)
    t.status=4
    t.challenged_at=START
    c._record_review=lambda i,n,challenge:None
    if final=='SATISFIED':
        payee=setup[1]._instance._task(1,0).recipient
        c.bonds_locked-=bond
        c.bonds_returned+=bond
    else:
        payee=setup[1]._instance._grant(1).sponsor
        c.bonds_locked-=bond
        c.bonds_forfeited+=bond
    c.bond_credits[payee]=bond
    c.total_bond_credits+=bond
    t.bond=0
    c._store(t)
    assert c.get_accounting()[ledger]==bond
    assert c.get_accounting()['bonds_locked']==0
    beneficiary=setup[4] if final=='SATISFIED' else setup[3]
    assert c.get_bond_credit(beneficiary)==bond
    vm.sender=beneficiary
    vm.origin=beneficiary
    c.claim_bond_credit()
    assert setup[0].transfers[-1][1:]==(bond,'finalized')
    assert setup[0].transfers[-1][0].as_bytes==bytes(beneficiary)
    conservation(c)


def test_inconclusive_challenge_recovery_and_refund(setup):
    c=fund(setup)
    provisional(setup,label='SATISFIED')
    vm=setup[0]
    vm.sender=setup[3]
    vm.origin=setup[3]
    vm.value=2*10**15
    c.challenge_task(1,0,'Evidence is ambiguous')
    vm.value=0
    mocks(vm,'INCONCLUSIVE')
    c.resolve_challenge(1,0)
    assert c.get_task(1,0).status==4
    warp(vm,START+86400)
    c.recover_stalled_challenge(1,0)
    assert c.get_accounting()['bonds_returned']==2*10**15
    assert c.get_bond_credit(setup[3])==2*10**15
    vm.sender=setup[3]
    vm.origin=setup[3]
    c.claim_bond_credit()
    assert setup[0].transfers[-1][1:]==(2*10**15,'finalized')
    assert c.get_task(1,0).status==6
    assert c.get_task(1,0).final_label=='SATISFIED'
    assert c.get_task(1,0).refunded==0
    assert c.get_accounting()['remaining']==AMOUNT
    conservation(c)
