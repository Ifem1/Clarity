# Release gates (do not claim DONE until all pass)

## Artifact-generation verification

- [x] Python contract syntax compiles; full local suite passes, 76 tests (55 offline + 21 GenLayer Direct Mode).
- [x] Pure frontend protocol suite passes, 11 tests.
- [x] Repo-local GenLayer CLI version is 0.39.1; installed GenVM linter is 0.11.0.
- [x] GenVM linter AST checks, SDK semantic validation and schema extraction pass against the source's pinned dependency hash. Generated ABI: `evidence/contract-schema.json`.
- [x] GenLayer Direct Mode public-method suite passes, 21 tests on installed `genlayer-test==0.29.2` and SDK dependency `v0.2.12`.
- [x] Direct Mode observes requested transfer messages for claims, refunds and bonds; it does not execute child transfer messages or prove rollback/atomicity.
- [ ] GenVM linter Pyright typecheck — BLOCKED: linter tries to write its SDK cache to `C:\Users\DELL\.cache\genvm-linter`, outside the workspace's writable roots.
- [ ] Frontend clean-install/typecheck/lint/build — BLOCKED: `npm ci` in a clean isolated directory stalled without completing; `npm ping` also stalled. Existing partial `node_modules` lacks `tsc`/`next` and the `next/core-web-vitals` ESLint config. Frontend protocol tests (11) pass.
- [ ] Native transfer failure atomicity and failed recipient recovery — NOT VERIFIED by Direct Mode or on chain. Pinned SDK documents receiver-side `__on_errored_message__` for failed incoming transfers, but no callback for failed outgoing child transfers. The contract marks payout/refund/bond settlement before emitting its finalized child transfer, so recipient rejection can leave contract accounting settled while native value was not received.
- [ ] Source-matched StudioNet contract deployment — NOT DEPLOYED; blocked pending complete frontend gates and safe native transfer failure handling.
- [ ] Two complete native GEN payout/refund/bond live scenarios — NOT EXECUTED.
- [ ] Live injected wallet writes and release pages — NOT EXECUTED.
- [ ] CI workflow green on final commit — NOT EXECUTED.

Every checked box must correspond to a real executed gate. No fake screenshots, results, hashes, time-travel or simulated live transactions.

## Mandatory agent closure order

1. Read architecture + security; inspect the entire current source. Do not change core scope.
2. Install `genlayer@0.39.1` repo-local. Check runtime SDK/GenVM pinned dependency support; make narrowly justified compatibility changes only. Complete GenVM validation and Direct Mode tests (including live sender/payable behavior, native transfers, revert semantics, consensus error behavior).
3. Install frontend dependencies; generate a genuine `frontend/package-lock.json`. Run `npm ci`, `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`. Fix any TypeScript/JS issues. Update CI to use `npm ci` and ensure green runs.
4. Review `docs/SECURITY.md`, implement additional adversarial and mutation tests for unexpected deployment semantics, and rerun entire suite.
5. Deploy one canonical contract on **Studionet 61999** with authorised unlocked test wallet only after the native-transfer failure path is made safe and all prior gates pass; capture actual contract source SHA-256, explorer address and deploy tx. Use no Studio-next/dev chain 61997.
6. Point Vercel to that exact address by setting `NEXT_PUBLIC_CLARITY_CONTRACT`, then manually deploy. No hidden signing server, no backend and no GitHub automatic deploy requirement.
7. Run reviewer matrix scenarios using actual unlocked CLI wallets and as much browser verification as available. No dummy data. Maintain source-matched `docs/LIVE_VERIFICATION.md`.
8. Freeze, push source and evidence to the exact new GitHub repository supplied by the owner, capture CI run; do not invent target repo or claim pushes if not authorised.

If any essential gate fails, report exact failure; do not declare submission ready.
