# Release gates

Current recovery deployment: `0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F` on StudioNet (chain 61999). It has one grant created from the local frontend as a payable smoke test. The scripted full lifecycle evidence is on the earlier lifecycle deployment.

## Verified locally and on StudioNet

- [x] Python contract compiles; full Python suite passes (89 tests, including 32 Direct Mode tests).
- [x] Frontend typecheck, ESLint, protocol tests (13/13), and optimized production build pass on 2026-10-21.
- [x] Deployment-time GenVM validation and remote schema extraction passed (24 public methods: 10 views, 14 writes); schema is recorded in `evidence/contract-schema.json`. A local linter rerun could not load its pinned SDK archive from cache.
- [x] Remote StudioNet schema read succeeds after a contract-level compatibility fix for the runner's two protocol handlers.
- [x] Recovery deployment succeeded; fresh reads show grant count 0 and all accounting fields 0.
- [x] Local frontend points to the recovery deployment; the optimized production build reads the recovery deployment successfully at `http://127.0.0.1:3002`; explorer evidence confirms the later payable grant submission.
- [x] `pore-test` and `chronicle-test-wallet` registered on the recovery deployment. Their registered-state reads both return true.
- [x] Local production frontend submitted a 0.00004 GEN payable `create_grant` call to the recovery deployment; explorer shows transaction `0xaae29915208d406cb31b11d4de5136346e644fc1d8e0df565464969cc533516c` as FINALIZED / SUCCESS and contract balance 0.00004 GEN. This is a frontend submission smoke test, not a full-cycle test; details are in `docs/LIVE_VERIFICATION.md`.

## Remaining release steps

- [x] Explicitly accept the live failed-child callback gap as a documented residual limitation. Two 0.0001 GEN child calls failed on StudioNet, including a plain native transfer, but neither instrumented sender nor receiver recorded a callback credit. Clarity restricts sponsors and payout recipients to direct EOAs, but this does not prove that a failed transfer to an EOA will recover; do not claim general outgoing-transfer recovery is safe. See `docs/LIVE_VERIFICATION.md` and `docs/SECURITY.md`.
- [x] Full grant lifecycle is covered by the existing scripted live scenarios on the earlier lifecycle deployment, with transaction/state evidence in `docs/LIVE_VERIFICATION.md`. The recovery deployment received a separate frontend-only grant-creation smoke test; it has not been taken through the lifecycle.
- [ ] Owner deploys the frontend to Vercel and verifies public reads against `0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F`.
- [ ] Push source and final live evidence to `https://github.com/Ifem1/Clarity.git` ; keep the callback limitation explicit in the release notes and record CI.

No Vercel deployment has been performed. Set `NEXT_PUBLIC_CLARITY_CONTRACT=0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F` in Vercel after reviewing the callback limitation.
