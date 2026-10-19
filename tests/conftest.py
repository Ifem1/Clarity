"""Strictly offline state-model harness; NOT GenVM Direct Mode.
Real GenVM tests and live chain proofs must be completed by the deployment agent.
"""
import sys
import types
import importlib.util
import datetime
from pathlib import Path
import pytest

class Address(str):
    def __new__(cls, value):
        v = str(value).lower()
        assert len(v) == 42 and v.startswith('0x') and all(c in '0123456789abcdef' for c in v[2:]), 'invalid address'
        return str.__new__(cls, v)

class Return:
    def __init__(self, calldata): self.calldata = calldata

class Public:
    def __init__(self):
        self.write = self
        self.view = self
        self.payable = self
    def __call__(self, fn): return fn

class Contract:
    def __new__(cls):
        instance = object.__new__(cls)
        instance.grants = {}
        instance.tasks = {}
        instance.manifests = {}
        instance.recipient_registry = {}
        return instance

@pytest.fixture
def env():
    user = '0x' + 'a' * 40
    beneficiary = '0x' + 'b' * 40
    other = '0x' + 'c' * 40
    public = Public()
    transfers = []
    message = types.SimpleNamespace(sender_address=Address(user), origin_address=Address(user), value=0)
    now = [datetime.datetime(2026, 10, 19, 12, tzinfo=datetime.timezone.utc).timestamp()]
    vm = types.SimpleNamespace(Return=Return, UserError=RuntimeError)

    def contract_interface(cls):
        class Recipient:
            def __init__(self, to): self.to=to
            def emit_transfer(self, value): transfers.append((self.to, value))
        return Recipient

    gl = types.SimpleNamespace(Contract=Contract, public=public, vm=vm, message=message,
                               message_raw={'datetime': ''},
                               evm=types.SimpleNamespace(contract_interface=contract_interface))
    module = types.ModuleType('genlayer')
    module.gl = gl
    module.allow_storage = lambda cls: cls
    module.Address = Address
    module.TreeMap = dict
    module.u256 = int
    module.u8 = int
    module.u16 = int
    sys.modules['genlayer'] = module
    location = Path(__file__).resolve().parents[1]/'contracts'/'clarity.py'
    spec = importlib.util.spec_from_file_location('clarity_under_test', location)
    c = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = c
    spec.loader.exec_module(c)

    def set_now(seconds=None):
        if seconds is not None: now[0] = seconds
        gl.message_raw['datetime'] = datetime.datetime.fromtimestamp(now[0], tz=datetime.timezone.utc).isoformat()
    set_now()
    yield types.SimpleNamespace(c=c, gl=gl, sender=Address(user), recipient=Address(beneficiary),
                                third=Address(other), transfers=transfers, now=now, set_now=set_now)
    sys.modules.pop('genlayer',None)
    sys.modules.pop('clarity_under_test',None)
