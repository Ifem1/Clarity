# Clarity architecture (locked source scope)

## Single authority

```
injected wallet browser (EIP-1193)
    | reads / GEN-funded writes (Studionet 61999)
    v
contracts/clarity.py
    |- grants: sponsor, amount, deadline, challenge window
    |- tasks: 2–8 fixed allocations, recipients, evidence sources, deps
    |- manifests: immutable primary/challenge round commitments
    |- native GEN custody: remaining + claimed + refunded
    |- challenge bond reserve: locked + returned + forfeited
    `- independent validators: fetch -> classify -> exact consensus
```

The frontend and outside evidence publishers cannot change the authorized release amounts, money recipients, deadlines or dependency edges. No off-chain infrastructure has transaction/signing or adjudication authority. The UI is an optional public client of on-chain methods.

## Ordered dependency graph

2–8 tasks ordered during creation. Each node may only depend on indices lower than its own. This proves acyclicity without a recursive on-chain search. Allocation basis points sum to exactly 10,000 and each amount is fixed at creation. Integer rounding remainder belongs to the last node. Graph nodes cannot be edited after creation.

A primary SATISFIED result is only *provisional* until the challenge period closes or resolves. Final SATISFIED becomes READY if all prerequisites are already READY/CLAIMED; otherwise SATISFIED_BLOCKED. `activate_task` is permissionless and requires every direct prerequisite READY/CLAIMED. Because each prerequisite is itself recursively gated, this suffices for the transitive graph. `claim_task` can be called by anyone but transfers only to the original recipient.

## Evidence authority and consensus

At creation task stores mandatory primary + corroborating HTTPS sources from distinct parent-domain approximations. Both sources must be independently accessed. Optional challenge-only sources are also frozen and cannot overlap with the original publisher identities. Source roles are immutable. The same URL is not assumed to contain immutable bytes; instead the primary review stores the digest of the bounded rendered text and the challenge must find unchanged primary text to generate a payable outcome. For reliable demos choose content-addressed or commit-pinned URLs from independent origins.

The leader and each validator fetch every frozen URL inside `run_nondet_unsafe`, hash ordered URL / successful-fetch flag / bounded rendered text, and independently request one of `SATISFIED`, `VIOLATED`, `INCONCLUSIVE`. The return is one simple string `TOKEN|<64 hex primary hash>|<64 hex combined hash>`. Validators require exact string match; thus the semantic verdict and evidence snapshots must agree. No arbitrary model payout is ever parsed. `INCONCLUSIVE`, `SOURCE_UNAVAILABLE` and `MODEL_OUTPUT_INVALID` are RETRYABLE, never payable.

The source bundle hash is not a proof that the source publisher is honest, nor that a claim is true. Strict byte agreement can occasionally produce `UNDETERMINED` if external content is unstable; this is deliberate fail-closed behaviour. Reviewer test evidence should include a stable and a conflicting snapshot.

## Settlement and liveness

| Input state | Allowed action | Result |
|---|---|---|
| AWAITING | recipient submit_task by deadline | SUBMITTED |
| SUBMITTED / RETRYABLE | permissionless evaluate_task within deadline+7d, at most 3 attempts | PROVISIONAL or RETRYABLE |
| PROVISIONAL | eligible adverse party challenge_task with exact 5% bond | CHALLENGED |
| PROVISIONAL after challenge window | finalize_task | SATISFIED_BLOCKED/READY or REJECTED |
| CHALLENGED | resolve_challenge within 24h (max 3 attempts) | final verdict or still CHALLENGED |
| CHALLENGED after 24h | recover_stalled_challenge | bond returned, RETRYABLE (never pays unagreed result) |
| SATISFIED_BLOCKED | activate_task if all deps final/eligible | READY |
| READY | permissionless claim_task | CLAIMED, funds delivered only to recipient |
| REJECTED | permissionless refund_task | REFUNDED to original sponsor |
| AWAITING/SUBMITTED/RETRYABLE/SATISFIED_BLOCKED after deadline+7d | refund_task | REFUNDED to sponsor |

A challenged result never transitions to a payout on timeout alone. Stalled-challenge recovery returns the bond, invalidates the provisional state and permits re-evaluation (if the original review cap and grace permit it) or eventual refund. A legitimate but blocked award whose prerequisites never become payable can be refunded after grace. An unclaimed READY award belongs to its recipient indefinitely; sponsor cannot confiscate it.

## Economic invariant

For each grant `total = remaining + paid + refunded`, and across all grants same for global escrow counters. Challenge reserve is separate: `bonds_received = bonds_locked + bonds_returned + bonds_forfeited`.

Any user may initiate settlement functions, but no caller can select payout address or amount: both are frozen at creation. State and ledgers update before `emit_transfer`; failed native transfer must revert the operation atomically (verify on the real GenVM).

## Non-features

No general NFT/marketplace, ERC-20, USDC, voting token, private evidence, confidential documents, arbitrary file upload, third-party signers, off-chain oracle verdicts, DAO governance layer, reputation system, backend/Worker/DB, external authentication or future-version roadmap.
