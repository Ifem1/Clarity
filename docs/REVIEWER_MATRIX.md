# Reviewer matrix / proof requirements

Target: exceptional GenLayer fit, contract quality, engineering and frontend. No point score guaranteed.

| Criterion | Concrete source | Acceptance evidence |
|---|---|---|
| GenLayer necessity | `contracts/clarity.py::_review` | Independent validator evidence fetches and semantic agreement are recorded in finalized StudioNet evaluations; disagreement rolls back without committing a manifest. |
| Economic substance | payable `create_grant`, `claim_task`, `refund_task` | Canonical escrow funded 0.20 GEN, paid 0.16, refunded 0.04, remaining 0; recipient balance deltas match 0.04 and 0.12 GEN; contract balance is zero. |
| Novelty | dependency graph + multi-recipient payout | Live task 1 reached `SATISFIED_BLOCKED` until task 0 became `READY`, then activated and paid; both recipients received their exact allocations. |
| Custom consensus | `run_nondet_unsafe(inspect,validate)` | Direct Mode tests pass; live majority success, disagreement, and no-majority cancellation/retry are recorded with transaction hashes. |
| Trust model | immutable sources, opponents can challenge | Frozen NASA and Smithsonian sources support the accepted/rejected claims; challenge manifest and 0.002 GEN bond outcome are recorded. |
| No admin settlement | only creator sponsor stored, no privileged payout method | Live recipients claimed directly; rejected task refund returned to sponsor under contract rules. |
| Adversarial design | bond exactness, wrong sender, retries, forced failure | Direct Mode assertions and live challenge, disagreement, no-majority and retry evidence pass. Registered direct EOAs avoid recipient-controlled transfer reverts; test deployment incident is disclosed in `LIVE_VERIFICATION.md`. |
| Frontend | `/`, `/new`, `/register`, `/grants/[id]` | Protocol tests, TypeScript, ESLint and optimized production build pass in a clean isolated install configured to the canonical address. Injected-wallet browser proof remains pending owner Vercel deployment. |
| Documentation | README, architecture, security, runbooks | Source hash, local checks, canonical address, finalized receipts, live ledger, and known test deployment loss are recorded. |

## Essential live scenarios

A. **Successful DAG**: StudioNet grant funded at 0.10 test GEN with 40%/60% task allocations. Both tasks were assessed SATISFIED; task 1 remained `SATISFIED_BLOCKED` until task 0 became READY, then both recipients claimed exactly 0.04 and 0.06 GEN.

B. **Rejected payout**: a separate 0.10 test GEN grant used a false July 17 Apollo 11 launch requirement contradicted by frozen evidence. Validators decided VIOLATED, recipient challenged with the exact 5% / 0.002 GEN bond, challenge upheld VIOLATED, sponsor received the forfeited bond and refunded the rejected 0.04 GEN. The other 0.06 GEN task was independently settled.

C. **Source/consensus failure**: live validator disagreement and a no-majority cancellation left tasks SUBMITTED with zero attempts and no committed manifest. Later evaluations recovered; failures never transitioned directly to READY or CLAIMED.

For every live operation, `docs/LIVE_VERIFICATION.md` records transaction hashes, finality/execution results, relevant source digests, balance deltas and final accounting. Finalized alone is not counted as successful execution.

**Current gate:** contract and local release checks plus live scenarios A/B/C are complete on canonical StudioNet contract `0x449f08f7407559D3e7538979B666D08ec35536B8`. Final source push/CI recording remains, followed by the owner’s Vercel deployment and injected-wallet browser verification. Two disposable test deployments stranded 0.20 testnet GEN after failed payable test calls; this is disclosed in the live verification record and does not affect canonical accounting, which is fully settled.
