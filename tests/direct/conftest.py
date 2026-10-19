"""Windows compatibility for genlayer-test 0.29.2's stdin injection.

Windows cannot unlink an open stdin file. Defer only that cleanup until the VM
has restored stdin; leave SDK execution, storage and consensus hooks unchanged.
"""
import os
from pathlib import Path
from unittest.mock import patch
import pytest


@pytest.fixture(autouse=True)
def windows_stdin_cleanup(monkeypatch):
    if os.name != 'nt':
        yield
        return
    from gltest.direct import loader
    original = loader._inject_message_to_fd0
    unlink = os.unlink
    pending = []

    def defer_open_file(path, *args, **kwargs):
        try:
            unlink(path, *args, **kwargs)
        except PermissionError as exc:
            if exc.winerror != 32:
                raise
            pending.append(Path(path))

    def inject(vm):
        with patch('os.unlink', defer_open_file):
            original(vm)

    monkeypatch.setattr(loader, '_inject_message_to_fd0', inject)
    yield
    for path in pending:
        try:
            unlink(path)
        except PermissionError:
            pass  # VM teardown may run later; the OS temporary file is harmless.


@pytest.fixture(autouse=True)
def capture_finalized_transfers(direct_vm, monkeypatch):
    """Record GenVM's actual PostMessage transfer intents in Direct Mode.

    The SDK emits transfer messages through WASI gl_call. genlayer-test exposes
    storage and time but does not execute child messages or change balances, so
    this verifies the exact finalized recipient/value request only.
    """
    from gltest.direct import wasi_mock
    transfers=[]
    original=wasi_mock.gl_call
    def capture(data):
        try:
            from genlayer.py import calldata
            request=calldata.decode(data)
        except Exception:
            return original(data)
        if isinstance(request,dict) and 'EthSend' in request:
            message=request['EthSend']
            if message.get('calldata')==b'' and message.get('value',0)>0:
                transfers.append((message['address'],int(message['value']),'finalized'))
        return original(data)
    direct_vm.transfers=transfers
    monkeypatch.setattr(wasi_mock,'gl_call',capture)
