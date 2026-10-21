"""Real GenVM deployment smoke/regression tests.

Do not confuse these with offline emulated tests; requires genlayer-test and
its pytest fixtures. Run and expand during release closure before any claim of
live protocol compatibility.
"""
import importlib.util
import json
import pytest

if importlib.util.find_spec('gltest') is None:
    pytest.skip('gltest Direct Mode runtime is unavailable locally', allow_module_level=True)

pytestmark = pytest.mark.direct


def deploy(direct_deploy):
    return direct_deploy('contracts/clarity.py', sdk_version='v0.2.12')


def test_deploy_counter(direct_deploy):
    c=deploy(direct_deploy)
    assert int(c.get_grant_count())==0
    assert int(c.get_accounting()['funded'])==0


def test_source_methods_exposed(direct_deploy):
    c=deploy(direct_deploy)
    assert c.get_status_names()[0]=='AWAITING'
    assert 'CLAIMED' in c.get_status_names()


def test_unknown_id_fails(direct_deploy):
    c=deploy(direct_deploy)
    with pytest.raises((AssertionError,Exception)):
        c.get_grant(99)


def test_incorrect_escrow_rejected(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=deploy(direct_deploy)
    direct_vm.warp('2026-10-19T12:00:00Z')
    direct_vm.sender=direct_alice
    direct_vm.origin=direct_alice
    direct_vm.value=1
    a='0x'+bytes(direct_bob).hex()
    # Two independent publisher identities. No web calls are made on creation.
    rows=[
       {'title':'Task A','requirement':'Data release exists','recipient':a,'allocation_bps':4000,'dependencies':[],'sources':[{'url':'https://alpha.example.org/x','role':'PRIMARY','required':True},{'url':'https://beta.example.net/y','role':'CORROBORATING','required':True}],'challenge_sources':[]},
       {'title':'Task B','requirement':'Results reproduced','recipient':a,'allocation_bps':6000,'dependencies':[0],'sources':[{'url':'https://gamma.example.com/x','role':'PRIMARY','required':True},{'url':'https://delta.example.edu/y','role':'CORROBORATING','required':True}],'challenge_sources':[]}
    ]
    c.create_grant('Fund reproducibility','Two independent milestones',1792497600,300,10**18,json.dumps(rows))
    assert c.get_grant_count()==0
    assert c.get_funding_recovery(direct_alice)==1
