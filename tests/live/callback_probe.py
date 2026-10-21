# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Disposable StudioNet probe for the GenVM errored-message callback."""
from genlayer import *


class CallbackProbe(gl.Contract):
    credits: TreeMap[Address, u256]
    total_credits: u256

    def __init__(self):
        self.total_credits = u256(0)

    @gl.public.write
    def trigger(self, receiver: Address, value: u256):
        gl.get_contract_at(receiver).emit_transfer(value=value)

    @gl.public.write.payable
    def __on_errored_message__(self):
        owner = gl.message.origin_address
        value = gl.message.value
        previous = self.credits[owner] if owner in self.credits else u256(0)
        self.credits[owner] = previous + value
        self.total_credits += value

    @gl.public.view
    def get_credit(self, owner: Address) -> u256:
        return self.credits[owner] if owner in self.credits else u256(0)

    @gl.public.view
    def get_total_credits(self) -> u256:
        return self.total_credits
