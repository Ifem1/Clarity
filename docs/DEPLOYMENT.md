# Deployment runbook / blank evidence record

**Status:** Not deployed. Contract address and deployment tx intentionally omitted until verified.

Network `studionet`, chain ID `61999`, RPC `https://studio.genlayer.com/api`, explorer `https://explorer-studio.genlayer.com`, repo-local CLI `genlayer@0.39.1`.

1. Repo-local CLI 0.39.1, GenVM linter 0.11.0, and Direct Mode `genlayer-test==0.29.2` were found. GenVM AST checks, schema generation, pinned SDK semantic validation and 21 Direct Mode tests passed; its Pyright command is blocked by a protected user-profile cache path. Full local suite: 76 passed.
2. Run source parity checks, GenVM lint/schema/typecheck, Direct Mode suite, mutation tests, TypeScript/lint/frontend tests/build. Never deploy a red or unchecked source. The clean frontend install stalled because registry access did not return; TypeScript, ESLint and Next production build remain unverified.
3. Use CLI wallets that are already unlocked by their authorised owner. Do not embed keys in code, screenshots or shell history. Fund only small native testnet amounts.
4. Deploy `contracts/clarity.py` to **61999** and wait for successful finalized execution, after safe native transfer failure handling is implemented and all earlier release gates pass. Verify contract source hash matches the tested git commit and uploaded source.
5. Execute `get_grant_count()` and `get_accounting()` read checks against that contract. Confirm the canonical address and chain ID in all config.
6. Set Vercel `NEXT_PUBLIC_CLARITY_CONTRACT` to the confirmed address, then deploy the `frontend` directory using the real Node/Next toolchain.
7. Verify the public site is open without wallet, shows live no-record state on fresh chain, and accepts an injected wallet. Test changed account/chain and refused network switch.
8. Execute the scenario matrix in `docs/REVIEWER_MATRIX.md` with small GEN. Capture tx, consensus finality, GenVM execution result, frozen source digests, manifests, grant/task states, payments/refunds/bonds. Update `docs/LIVE_VERIFICATION.md` and the README canonical section with real links only after proof.

## Final immutable deployment record (to complete after actual deployment)

```text
Git commit: NOT_DEPLOYED
Source SHA-256: pending final source freeze (last preflight before additional tests/docs: `3f17062d9c979fc4225b3938c314a3929ee189f003c2d15fabbf64e23975cb4d`)
Contract: NOT_DEPLOYED
Deployment transaction: NOT_DEPLOYED
Consensus: NOT_DEPLOYED
Execution: NOT_DEPLOYED
Production frontend: NOT_DEPLOYED
Final CI run: NOT_EXECUTED

Deployment remains gated on frontend clean-install/typecheck/lint/build and a safe design for outgoing transfer failures. The pinned GenVM runtime has a callback for failed incoming payable messages but exposes no corresponding contract callback for failed outgoing child transfers; Clarity currently settles claim/refund/bond storage before emitting those child transfers. Do not deploy this version with recipient-controlled failure paths unresolved.
```
