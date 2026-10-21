# Security and assumptions

## Trust boundaries

- Only the chain-stored grant and tasks are authoritative for recipients, amounts, DAG edges, statuses, challenge deadlines and refundable value.
- Only GenLayer validators' independently replicated nondeterministic review can classify frozen public evidence. The AI **cannot** create new task IDs, change percentage allocations, change addresses, invent funding, set deadlines, or move funds directly.
- A source named `PRIMARY` remains an external publisher. Using two different hostnames does not guarantee two independent legal operators. Source quality and licensing must be reviewed before a sponsor funds the grant.
- The complete rendered text (up to 2,200 characters per source) used for a provisional decision is stored in its public manifest. Challenge review reuses that historical primary snapshot, so later publisher edits cannot replace the evidence supporting the provisional result. Larger rendered sources fail closed and cannot produce a payout.
- Challenge evidence is intentionally closed: source URLs are selected at funding, and a challenge accepts only a bounded rationale. The challenger cannot introduce or substitute URLs. Challenge-only URLs are fetched at challenge time; if a required one is unavailable or the challenge cannot resolve, recovery returns the original provisional decision rather than making the allocation refundable.
- `SATISFIED_BLOCKED` can be refunded after the deadline grace only while at least one prerequisite is still not `READY` or `CLAIMED`. If prerequisites are satisfied, activation remains available and refund is prohibited. If a blocked allocation is refunded before a late prerequisite becomes ready, the refund is final and that allocation cannot be reactivated.
- All public evidence, including challenge notes, is untrusted. It may contain model-directed prompt injection; prompt instructions explicitly forbid obeying data instructions. Validator agreement is not proof of semantic truth. An `INCONCLUSIVE` rather than an invented success is expected for unclear evidence.

## Threat scenarios

| Threat | Mitigation | Still to verify on chain |
|---|---|---|
| Unauthorised claims | fixed recipient + READY state | actual GEN transfer recipient |
| Over-allocation / bps rounding | fixed total 10,000 bps; last-node dust | zero conservation residual |
| Cyclic prerequisites | backwards-only sorted unique deps | malicious graph rejection |
| Fake model payout | only semantic label parsed | prompt injection doesn't settle |
| Contradictory source bytes | full bounded rendered text is hashed and stored in the exact validator result | oversized documents fail closed; no late page section is silently discarded |
| Sponsor changes publisher after provisional success | challenge reads the committed primary text snapshot | new content at that URL is not considered in that challenge |
| Challenge source unavailable or validators cannot resolve | original provisional result is finalized after the recovery timeout | conservative fallback favors the already-consensed provisional decision; the challenger receives their bond back |
| Evidence-source substitution | URLs stored only at creation and displayed before funding/challenging | no new challenge URLs are admitted |
| Challenge griefing | 5% bond and bounded challenges | bond success/failure credits |
| Stalled consensus | RETRYABLE, 3 attempts, 7-day grace; stalled challenge recovery credits bond | no stuck accounting |
| Recipient transfer reverts | only directly registered EOAs can receive; contract includes origin-owned callback recovery | accepted residual limitation: controlled StudioNet failures produced no callback credit, including failed native transfer; even EOA payout recovery remains unproven |
| Duplicate claim/refund | terminal statuses and paid/refunded guards | replay rejection |
| Wallet account/chain change | EIP-1193 event clears session, chain validated | real injected-wallet browser proof |
| Sponsor after-the-fact refund | READY/CLAIMED and dependency-ready `SATISFIED_BLOCKED` disallowed | dependency must be checked atomically in the refund method |
| Invalid payable grant input | expected validation errors create an origin-owned recovery credit and do not revert | fatal VM/ABI failures before the recovery code runs are outside the contract guarantee |
| DNS rebinding/private routing | HTTPS and literal private-target rejects; GenVM renderer sandbox | document residual SSRF limits |

## Native transfer boundary

The pinned GenVM SDK defines `__on_errored_message__`, and Clarity credits the transaction origin for owner-only recovery. However, two live StudioNet child messages carrying 0.0001 GEN failed and produced no callback credit in instrumented sender or receiver contracts, including a plain native transfer. Direct Mode only simulates the handler, so `recover_failed_transfer` is not proven to recover live failed sends. This gap is explicitly accepted as a residual limitation for this release: do not claim general outgoing-transfer recovery is safe or proven, even when payout recipients are registered EOAs. Challenge bond outcomes accrue to a separate origin-owned pull credit claimed with `claim_bond_credit`.

Beneficiaries and sponsors must register or act from direct EOA transactions (`sender_address == origin_address`), excluding contract wallets and forwarding contracts. Accounting is updated before outgoing messages; a delivered error callback credits the refunded value for retry. Unknown selectors with value use the payable fallback. Fatal ABI decoding, runtime aborts and empty-calldata transfers that do not dispatch to a supported payable handler cannot be safely credited by application code.

## Known boundaries

- StudioNet native GEN is testnet value; this is not production stablecoin custody.
- No legal arbitration or real-world enforceability is represented.
- A source render over 2,200 characters is rejected, even if decisive evidence is present; sponsors must point to concise authoritative records.
- Expected create-grant validation errors and unknown-selector value calls create origin-owned recovery credits. ABI decoding failures, fatal VM/OOG failures and plain transfers without an implemented receive handler remain outside that guarantee. Failed outgoing transfers are recoverable only if GenVM delivers the documented errored-message callback; live StudioNet failures showed no callback credit, so recovery remains unproven and is an accepted release limitation.
- No arbitrary loops or downstream transfer instructions are accepted.
- Full contract source and frontend must be checked against installed pinned GenVM SDK before deployment. Offline state-model tests are *not* a substitute for Direct Mode or live finality.
- The current funding/reward architecture has a small on-chain state footprint per grant but not constant-cost global enumeration. The browser lists only the latest 30 grants and does not promise scalable global indexing without an indexer.
