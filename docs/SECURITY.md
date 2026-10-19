# Security and assumptions

## Trust boundaries

- Only the chain-stored grant and tasks are authoritative for recipients, amounts, DAG edges, statuses, challenge deadlines and refundable value.
- Only GenLayer validators' independently replicated nondeterministic review can classify frozen public evidence. The AI **cannot** create new task IDs, change percentage allocations, change addresses, invent funding, set deadlines, or move funds directly.
- A source named `PRIMARY` remains an external publisher. Using two different hostnames does not guarantee two independent legal operators. Source quality and licensing must be reviewed before a sponsor funds the grant.
- The first observed primary text digest is fixed at the provisional review; a challenge can only produce a new payable decision if that text is unchanged. Distinct challenge sources are preauthorised and cannot replace primaries. Source URL freezing alone does not make publisher data immutable.
- All public evidence, including challenge notes, is untrusted. It may contain model-directed prompt injection; prompt instructions explicitly forbid obeying data instructions. Validator agreement is not proof of semantic truth. An `INCONCLUSIVE` rather than an invented success is expected for unclear evidence.

## Threat scenarios

| Threat | Mitigation | Still to verify on chain |
|---|---|---|
| Unauthorised claims | fixed recipient + READY state | actual GEN transfer recipient |
| Over-allocation / bps rounding | fixed total 10,000 bps; last-node dust | zero conservation residual |
| Cyclic prerequisites | backwards-only sorted unique deps | malicious graph rejection |
| Fake model payout | only semantic label parsed | prompt injection doesn't settle |
| Contradictory source bytes | byte digests in exact validator result | no-majority does not commit |
| Evidence-source substitution | URLs stored only at creation | challenges use frozen authorities |
| Challenge griefing | 5% bond and bounded challenges | bond success/failure transfers |
| Stalled consensus | RETRYABLE, 3 attempts, 7-day grace; stalled challenge recovery | no stuck accounting |
| Recipient transfer reverts | only directly registered EOAs can receive; contract-wallet forwarding is rejected | actual external-message delivery still requires live proof |
| Duplicate claim/refund | terminal statuses and paid/refunded guards | replay rejection |
| Wallet account/chain change | EIP-1193 event clears session, chain validated | real injected-wallet browser proof |
| Sponsor after-the-fact refund | READY/CLAIMED disallowed | no sponsor clawback |
| DNS rebinding/private routing | HTTPS and literal private-target rejects; GenVM renderer sandbox | document residual SSRF limits |

## Native transfer boundary

The pinned GenVM SDK has no callback that restores accounting after a failed outgoing child transfer, and failed child value is not automatically returned to its sender. Clarity mitigates recipient-controlled failures by requiring each beneficiary to register from a direct transaction where `sender_address == origin_address`; grant sponsors must also submit directly from an EOA. This excludes contract wallets and forwarding contracts, whose code could reject a transfer. A registered EOA has no recipient code to revert the native GEN transfer. The transfer remains asynchronous, and actual delivery and balance deltas still require a live StudioNet scenario.

## Known boundaries

- StudioNet native GEN is testnet value; this is not production stablecoin custody.
- No legal arbitration or real-world enforceability is represented.
- Strict source-text equality during challenge can cause unavailable evidence or no-majority on moving websites.
- No arbitrary loops or downstream transfer instructions are accepted.
- Full contract source and frontend must be checked against installed pinned GenVM SDK before deployment. Offline state-model tests are *not* a substitute for Direct Mode or live finality.
- The current funding/reward architecture has a small on-chain state footprint per grant but not constant-cost global enumeration. The browser lists only the latest 30 grants and does not promise scalable global indexing without an indexer.
