"""Adversarial offline state-model tests. Separate from GenVM Direct Mode proof."""
import json
import pytest
from test_protocol import create, tasks, source, H1, H2, H3, H4

@pytest.mark.parametrize('host',["https://localhost/x","https://127.0.0.1/a","https://10.0.0.1/b","https://172.16.2.2/x","https://172.31.255.2/x","https://100.64.12.4/x","https://192.168.8.1/x","https://0.0.0.0/a","https://example.org:8080/a","https://user@example.org/a","javascript:alert(1)","http://public.example.org/a"])
def test_unsafe_source_blocked(env,host):
    rows=tasks(env);rows[0]['sources'][0]['url']=host
    with pytest.raises((AssertionError,ValueError)):create(env,rows=rows)

@pytest.mark.parametrize('bps',[0,10001,-3,1.5,True,'5000'])
def test_bps_type_and_range(env,bps):
    rows=tasks(env);rows[0]['allocation_bps']=bps
    with pytest.raises((AssertionError,ValueError,TypeError)):create(env,rows=rows)

def test_duplicate_publisher_is_rejected(env):
    rows=tasks(env);rows[0]['sources'][1]['url']='https://data.example.org/mirror'
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_challenge_source_cannot_replace_primary(env):
    rows=tasks(env);rows[0]['challenge_sources'][0]['url']='https://sub.alpha.example.org/duplicate'
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_both_primary_and_corrob_required(env):
    rows=tasks(env);rows[1]['sources'][1]['required']=False
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_role_challenge_not_allowed_on_base_source(env):
    rows=tasks(env);rows[0]['sources'][1]['role']='CHALLENGE'
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_challenge_sources_are_challenge_only(env):
    rows=tasks(env);rows[0]['challenge_sources'][0]['role']='PRIMARY'
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_zero_recipient_invalid(env):
    rows=tasks(env);rows[0]['recipient']='0x'+'0'*40
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_self_recipient_invalid(env):
    rows=tasks(env);rows[0]['recipient']=str(env.sender)
    with pytest.raises(AssertionError):create(env,rows=rows)

def test_nonrecipient_cannot_submit(env):
    t=create(env);env.gl.message.sender_address=env.third
    with pytest.raises(AssertionError):t.submit_task(1,0)

def test_second_submission_rejected(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    with pytest.raises(AssertionError):t.submit_task(1,0)

def test_inconclusive_no_provisional_or_claim(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'INCONCLUSIVE|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,0)
    assert t.get_task(1,0).status==env.c.RETRYABLE
    assert t.get_accounting()['remaining']==10**18
    with pytest.raises(AssertionError):t.claim_task(1,0)
    assert t.get_manifest(1,0,'PRIMARY',1).label=='INCONCLUSIVE'

def test_retry_cooldown_and_cap(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SOURCE_UNAVAILABLE|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,0)
    with pytest.raises(AssertionError):t.evaluate_task(1,0)
    env.now[0]+=61;env.set_now();t.evaluate_task(1,0)
    env.now[0]+=61;env.set_now();t.evaluate_task(1,0)
    env.now[0]+=61;env.set_now()
    with pytest.raises(AssertionError):t.evaluate_task(1,0)
    assert t.get_task(1,0).attempts==3

def test_wrong_challenge_bond_reverts(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'VIOLATED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,0)
    env.gl.message.value=1
    with pytest.raises(AssertionError):t.challenge_task(1,0,'The result is disputed')
    assert t.get_accounting()['bonds_locked']==0

def test_sponsor_cannot_challenge_violation(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'VIOLATED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,0)
    env.gl.message.sender_address=env.sender;env.gl.message.value=2*10**16
    with pytest.raises(AssertionError):t.challenge_task(1,0,'An adverse verdict to another party')

def test_recipient_cannot_challenge_satisfaction(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,0)
    env.gl.message.value=2*10**16
    with pytest.raises(AssertionError):t.challenge_task(1,0,'Already favorable')

def test_cannot_claim_provisional_even_after_window_without_finalizing(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,0)
    env.now[0]+=301;env.set_now()
    with pytest.raises(AssertionError):t.claim_task(1,0)

def test_refund_cannot_take_ready_allocation(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,0)
    env.now[0]+=301;env.set_now();t.finalize_task(1,0)
    env.now[0]+=10*86400;env.set_now()
    with pytest.raises(AssertionError):t.refund_task(1,0)

def test_blocked_allocation_eventually_refundable(env):
    t=create(env);env.gl.message.sender_address=env.third;t.submit_task(1,1)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,1)
    env.now[0]+=301;env.set_now();t.finalize_task(1,1)
    assert t.get_task(1,1).status==env.c.SATISFIED_BLOCKED
    env.now[0]+=9*86400;env.set_now();t.refund_task(1,1)
    assert t.get_accounting()['refunded']==6*10**17

def test_double_challenge_rejected(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64;t.evaluate_task(1,0)
    env.gl.message.sender_address=env.sender;env.gl.message.value=2*10**16
    t.challenge_task(1,0,'Dispute recorded')
    with pytest.raises(AssertionError):t.challenge_task(1,0,'Duplicate challenge')

def test_zero_deposit_fails(env):
    with pytest.raises(AssertionError):create(env,amount=0)

def test_accounting_recovery_after_timeout(env):
    t=create(env);env.now[0]+=9*86400;env.set_now()
    t.refund_task(1,0);t.refund_task(1,1)
    a=t.get_accounting();assert a['funded']==a['paid']+a['refunded']+a['remaining']
    assert a['refunded']==10**18
