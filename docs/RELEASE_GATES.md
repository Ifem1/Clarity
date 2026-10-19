# Release gates (do not claim DONE until all pass)

## Artifact-generation verification

- [x] Python contract syntax compiles; full local suite passes, 81 tests (57 offline + 24 GenLayer Direct Mode).
- [x] Pure frontend protocol suite passes, 11 tests.
- [x] Repo-local GenLayer CLI version is 0.39.1; installed GenVM linter is 0.11.0.
- [x] GenVM linter AST checks, SDK semantic validation and schema extraction pass against the source's pinned dependency hash. Generated ABI: `evidence/contract-schema.json`.
- [x] GenLayer Direct Mode public-method suite passes, 24 tests on installed `genlayer-test==0.29.2` and SDK dependency `v0.2.12`.
- [x] Direct Mode observes requested transfer messages for claims, refunds and bonds; it does not execute child transfer messages or prove rollback/atomicity.
- [x] Pyright typecheck against the locally installed pinned GenVM runner source — no type errors. (The linter wrapper was directed to that exact local SDK path because its default user-profile cache is protected.)
- [x] Clean frontend `npm ci`, typecheck, lint, protocol tests and production build pass in an isolated temporary install. Build output is source-matched; CSS autoprefixer warnings were fixed.
- [x] Recipient-controlled native transfer failure mitigated: sponsor creation and recipient registration require direct EOA-origin transactions; all task recipients must register before funding. A contract wallet cannot register or sponsor via a forwarding contract, so native payouts and refunds cannot be rejected by recipient code.
- [x] Canonical source-matched StudioNet deployment on chain 61999; finalized receipt and fresh reads recorded in `docs/DEPLOYMENT.md`.
- [x] Three live lifecycle scenarios executed: dependency payout and exact native deltas; VIOLATED review, exact 5% challenge bond, forfeiture and refund; validator disagreement/no-majority with unchanged state and successful retry. Receipts and limitations are recorded in `docs/LIVE_VERIFICATION.md`.
- [x] Local Chrome injected-wallet check: connected an already-authorized wallet, verified the app switched to StudioNet 61999 without a stale warning, and read the canonical grant and claimed task state. No transaction was submitted.
- [x] Release implementation commit `ca80a3ddca5349d6bae0ddbbe52b3e8a1ebb927b` pushed; GitHub Actions run [39301675436](https://github.com/Ifem1/Clarity/actions/runs/39301675436) passed all three jobs.
- [ ] Owner’s manual Vercel deployment and production URL verification — owner action.
- [ ] Injected-wallet browser test against the public deployment — local Chrome check passed; public URL check waits for Vercel deployment.

Two earlier disposable test deployments received malformed/unregistered payable calls and hold 0.10 GEN each with zero app-ledger accounting. They are not the canonical address and have no recovery method. The canonical contract is clean; the testnet loss is transparently recorded in `docs/LIVE_VERIFICATION.md`.

Every checked box must correspond to a real executed gate. No fake screenshots, results, hashes, time-travel or simulated live transactions.

## Mandatory agent closure order

1. Read architecture + security; inspect the entire current source. Do not change core scope.
2. Install `genlayer@0.39.1` repo-local. Check runtime SDK/GenVM pinned dependency support; make narrowly justified compatibility changes only. Complete GenVM validation and Direct Mode tests (including live sender/payable behavior, native transfers, revert semantics, consensus error behavior).
3. Install frontend dependencies; generate a genuine `frontend/package-lock.json`. Run `npm ci`, `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`. Fix any TypeScript/JS issues. Update CI to use `npm ci` and ensure green runs.
4. Review `docs/SECURITY.md`, implement additional adversarial and mutation tests for unexpected deployment semantics, and rerun entire suite.
5. Canonical contract has been deployed to **Studionet 61999**; deployment and transaction evidence are recorded. Use no Studio-next/dev chain 61997.
6. Point Vercel to that exact address by setting `NEXT_PUBLIC_CLARITY_CONTRACT`, then manually deploy. No hidden signing server, no backend and no GitHub automatic deploy requirement.
7. Run reviewer matrix scenarios using actual unlocked CLI wallets and as much browser verification as available. The live matrix and real transaction results are recorded in `docs/LIVE_VERIFICATION.md`.
8. Freeze and push source/evidence to `https://github.com/Ifem1/Clarity.git`, the exact destination supplied by the owner; capture the resulting CI run.

If any essential gate fails, report exact failure; do not declare submission ready.
