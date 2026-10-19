# Reviewer matrix / proof requirements

Target: exceptional GenLayer fit, contract quality, engineering and frontend. No point score guaranteed.

| Criterion | Concrete source | Acceptance evidence required |
|---|---|---|
| GenLayer necessity | `contracts/clarity.py::_review` | separate validators independently fetch source bytes and agree semantic label+digest; leader/validator disagreement rolls back |
| Economic substance | payable `create_grant`, `claim_task`, `refund_task` | before/after native GEN balances + exact escrow accounting |
| Novelty | dependency graph + multi-recipient payout | node 2 verified but BLOCKED while node 1 pending; later activates and pays |
| Custom consensus | `run_nondet_unsafe(inspect,validate)` | accepted and disagreed/undetermined receipts |
| Trust model | immutable sources, opponents can challenge | attempted source, recipient, amount, edge substitution rejected |
| No admin settlement | only creator sponsor stored, no privileged payout method | source + live outsider-initiated claims and refunds |
| Adversarial design | bond exactness, wrong sender, retries, forced failure | Direct Mode assertions and live paths |
| Frontend | `/`, `/new`, `/grants/[id]` | real wallet approval, no mocked records, role guards, correct decimals |
| Documentation | README, architecture, security, runbooks | source-matched canonical explorer URL, receipts, CI and evidence files |

## Essential live scenarios

A. **Successful DAG**: sponsor funds 0.10 test GEN split across 2 tasks (40%/60%); recipient(s) submit; tasks evaluate SATISFIED; verify downstream task stays SATISFIED_BLOCKED until parent becomes READY; finalise -> activate -> claim both. Check exact 0.04 + 0.06 GEN.

B. **Rejected payout**: a separate 0.10 test GEN grant, primary evidence explicitly contradicts task requirement; validators decide VIOLATED; recipient bonds 5% and challenges; if still VIOLATED the sponsor receives bond; sponsor refunds rejected task. Verify beneficiary did not receive the rejected allocation.

C. **Source/consensus failure**: a required source is inaccessible, evidence bytes differ across validators, or model returns malformed token; demonstrate no `READY` or `CLAIMED` transition. Exercise bounded retry and recovery. If it is impossible to induce a truthful live failure, record that limitation and leave test-only evidence labelled test-only.

For each successful live operation: finalized transaction hash, GenVM execution result, validator finality, exact method/args, task/grant before+after, source manifest, amount and recipient, global deltas. Record failed/undetermined transactions separately; *finalized* alone is not successful execution.
