# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Disposable StudioNet receiver that rejects an incoming native transfer."""
from genlayer import *


class Rejector(gl.Contract):
    credits: TreeMap[Address, u256]
    total_credits: u256

    def __init__(self):
        self.total_credits = u256(0)

    @gl.public.write.payable
    def __receive__(self):
        raise gl.vm.UserError("intentional callback probe rejection")

    @gl.public.write.payable
    def __on_errored_message__(self):
        origin = gl.message.origin_address
        amount = gl.message.value
        prior = self.credits[origin] if origin in self.credits else u256(0)
        self.credits[origin] = prior + amount
        self.total_credits += amount

    @gl.public.view
    def get_credit(self, origin: Address) -> u256:
        return self.credits[origin] if origin in self.credits else u256(0)

    @gl.public.view
    def get_total_credits(self) -> u256:
        return self.total_credits
