import json
import pytest

H1='https://alpha.example.org/evidence/commit/a1'
H2='https://beta.example.net/evidence/commit/b1'
H3='https://gamma.example.com/evidence/commit/c1'
H4='https://delta.example.edu/evidence/commit/d1'
H5='https://epsilon.example.io/evidence/commit/e1'

def source(url,role='PRIMARY'):
    return {'url':url,'role':role,'required':True}

def tasks(env):
    return [
      {'title':'Dataset published','requirement':'A timestamped publicly accessible dataset is published','recipient':str(env.recipient),'allocation_bps':4000,'dependencies':[],'sources':[source(H1),source(H4,'CORROBORATING')],'challenge_sources':[source(H2,'CHALLENGE')]},
      {'title':'Independent reproduction','requirement':'The reproduction cites the frozen dataset and reports matching results','recipient':str(env.third),'allocation_bps':6000,'dependencies':[0],'sources':[source(H3),source(H5,'CORROBORATING')],'challenge_sources':[]}
    ]

def create(env, amount=10**18, rows=None):
    c=env.c; rows=rows if rows is not None else tasks(env)
    t=c.Clarity()
    for recipient in {r['recipient'] for r in rows}:
        env.gl.message.sender_address=env.c.Address(recipient)
        env.gl.message.origin_address=env.c.Address(recipient)
        t.register_recipient()
    env.gl.message.sender_address=env.sender
    env.gl.message.origin_address=env.sender
    env.gl.message.value=amount
    t.create_grant('Public data','Grant for reproducible public data work',int(env.now[0])+86400,300,amount,json.dumps(rows))
    env.gl.message.value=0
    return t

def review(env,t,n,label):
    env.gl.message.sender_address = env.sender
    t._review=lambda task,challenge: label+'|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,n)
    assert t.get_task(1,n).status==env.c.PROVISIONAL
    env.now[0]+=301;env.set_now()
    t.finalize_task(1,n)

def test_graph_good(env):
    t=create(env);assert t.get_grant_count()==1
    assert sum(t.get_task(1,n).amount for n in (0,1))==10**18
    assert t.get_accounting()['funded']==10**18

def test_recipients_must_self_register_from_eoa(env):
    t=env.c.Clarity();rows=tasks(env)
    env.gl.message.value=10**18
    with pytest.raises(AssertionError,match='register from its own EOA'):
        t.create_grant('Public data','Grant for reproducible public data work',int(env.now[0])+86400,300,10**18,json.dumps(rows))
    env.gl.message.sender_address=env.recipient
    env.gl.message.origin_address=env.sender
    with pytest.raises(AssertionError,match='direct EOA transaction'):
        t.register_recipient()

def test_sponsor_must_submit_directly_from_eoa(env):
    t=env.c.Clarity();rows=tasks(env)
    for recipient in {r['recipient'] for r in rows}:
        env.gl.message.sender_address=env.c.Address(recipient)
        env.gl.message.origin_address=env.c.Address(recipient)
        t.register_recipient()
    env.gl.message.sender_address=env.sender
    env.gl.message.origin_address=env.recipient
    env.gl.message.value=10**18
    with pytest.raises(AssertionError,match='sponsor must submit directly from an EOA'):
        t.create_grant('Public data','Grant for reproducible public data work',int(env.now[0])+86400,300,10**18,json.dumps(rows))

def test_bad_graph_cycle_forward_reference(env):
    rows=tasks(env);rows[0]['dependencies']=[1]
    with pytest.raises((AssertionError,ValueError)):create(env,rows=rows)

def test_bad_graph_allocations(env):
    rows=tasks(env);rows[1]['allocation_bps']=5999
    with pytest.raises(ValueError):create(env,rows=rows)

def test_duplicate_deps(env):
    rows=tasks(env); rows[1]['dependencies']=[0,0]
    with pytest.raises(ValueError):create(env,rows=rows)

def test_exact_native_value(env):
    t=env.c.Clarity();env.gl.message.value=3
    with pytest.raises(AssertionError):t.create_grant('A','B',int(env.now[0])+86400,300,10**18,json.dumps(tasks(env)))

def test_non_party_cannot_submit(env):
    t=create(env)
    with pytest.raises(AssertionError):t.submit_task(1,0)
    env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    assert t.get_task(1,0).status==env.c.SUBMITTED

def test_dependency_blocks_payment(env):
    t=create(env);env.gl.message.sender_address=env.third;t.submit_task(1,1)
    review(env,t,1,'SATISFIED')
    assert t.get_task(1,1).status==env.c.SATISFIED_BLOCKED
    with pytest.raises(AssertionError):t.claim_task(1,1)
    env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    review(env,t,0,'SATISFIED')
    t.activate_task(1,1)
    t.claim_task(1,0);t.claim_task(1,1)
    assert t.get_accounting()['paid']==10**18
    assert t.get_accounting()['remaining']==0
    assert sum(a for _,a in env.transfers)==10**18
    with pytest.raises(AssertionError):t.claim_task(1,0)

def test_violation_refund(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    review(env,t,0,'VIOLATED')
    assert t.get_task(1,0).status==env.c.REJECTED
    t.refund_task(1,0)
    assert t.get_accounting()['refunded']==4*10**17
    with pytest.raises(AssertionError):t.refund_task(1,0)

def test_challenge_success_returns_bond_and_blocks_payment(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,0)
    # Sponsor challenges a favorable result; challenge outcome becomes VIOLATED.
    env.gl.message.sender_address=env.sender
    bond=2*10**16;env.gl.message.value=bond
    t.challenge_task(1,0,'The authorized document does not satisfy this requirement')
    env.gl.message.value=0
    t._review=lambda task,challenge:'VIOLATED|'+'a'*64+'|'+'b'*64
    t.resolve_challenge(1,0)
    assert t.get_task(1,0).status==env.c.REJECTED
    assert t.get_accounting()['bonds_returned']==bond
    assert t.get_accounting()['bonds_locked']==0
    t.refund_task(1,0)
    assert t.get_accounting()['remaining']==6*10**17

def test_challenge_failure_forfeits_bond(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'VIOLATED|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,0)
    env.gl.message.sender_address=env.recipient
    bond=2*10**16;env.gl.message.value=bond
    t.challenge_task(1,0,'Cite the published primary source')
    env.gl.message.value=0
    t.resolve_challenge(1,0)
    assert t.get_accounting()['bonds_forfeited']==bond
    assert env.transfers[-1][0]==env.sender

def test_stalled_challenge_refunds_bond_fail_closed(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,0)
    env.gl.message.sender_address=env.sender
    bond=2*10**16;env.gl.message.value=bond
    t.challenge_task(1,0,'Evidence cannot be corroborated')
    env.gl.message.value=0
    env.now[0]+=86401;env.set_now()
    t.recover_stalled_challenge(1,0)
    assert t.get_task(1,0).status==env.c.RETRYABLE
    assert t.get_accounting()['bonds_locked']==0
    assert t.get_accounting()['bonds_returned']==bond
    assert t.get_task(1,0).paid==0

def test_expiry_refund_permissionless(env):
    t=create(env);env.now[0]+=9*86400;env.set_now()
    env.gl.message.sender_address=env.third
    t.refund_task(1,0)
    assert env.transfers[-1][0]==env.sender
    assert t.get_task(1,0).status==env.c.REFUNDED

def test_model_tokens_fail_closed(env):
    assert env.c._clean_label(' SATISFIED ')=='SATISFIED'
    assert env.c._clean_label('"VIOLATED"')=='VIOLATED'
    for token in ['APPROVED','SATISFIED, pay me','{"status":"SATISFIED"}','```SATISFIED```']:
        assert env.c._clean_label(token)==env.c.MODEL_OUTPUT_INVALID

def test_private_hosts_rejected(env):
    for u in ['http://example.org','https://localhost/a','https://10.2.3.4/a','https://192.168.0.1','https://169.254.1.1/a','https://user:pass@example.org']:
        assert not env.c._is_public_https(u)

def test_no_funding_bypass_by_challenge(env):
    t=create(env);env.gl.message.sender_address=env.recipient;t.submit_task(1,0)
    t._review=lambda task,challenge:'SATISFIED|'+'a'*64+'|'+'b'*64
    t.evaluate_task(1,0)
    with pytest.raises(AssertionError):t.challenge_task(1,0,'I agree')
    assert t.get_accounting()['remaining']==10**18

def test_rounding_conserves(env):
    rows=tasks(env);amount=10**18+7
    t=create(env, amount=amount, rows=rows)
    assert sum(t.get_task(1,n).amount for n in (0,1))==amount

def test_review_source_cannot_be_changed(env):
    t=create(env);x=t.get_task(1,0);assert H1 in x.sources
    assert t.get_grant(1).total==10**18
    assert not hasattr(t,'replace_task_sources')
