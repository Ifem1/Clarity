# Live contract verification

**NOT EXECUTED / no real deployment.** No transactions, contract address, manifests or live claims are recorded here.

## Local test evidence (not live chain evidence)

- Offline state-model: 55 passed.
- GenLayer Direct Mode public-method suite: 21 passed using installed `genlayer-test==0.29.2` with the source-pinned GenLayer SDK dependency.
- Direct Mode observed exact `EthSend` native transfer requests for claims, refunds and bonds, including recipient, value and finalized setting. The fixture does not execute child transfers or model a recipient's receive handler, so this does not prove balance deltas, atomic rollback or recovery after transfer failure.
- A Direct Mode injected `EthSend` failure raises at the child-message hook after the contract has updated the parent task ledger. The test environment has no transaction-level storage rollback, so the observed residual ledger is a harness limitation and cannot establish actual chain behavior. Live GenVM failure atomicity is an essential unresolved gate.
- Frontend protocol utility suite: 11 passed. Typecheck, lint and production build remain unverified because repeated dependency installation did not complete cleanly.
- These results are local validation only. They do not satisfy Scenarios A, B or C below.

| Item | Scenario A: dependency unlock / payout | Scenario B: violated review / challenged refund | Scenario C: failure / recovery |
|---|---|---|---|
| Contract | pending | pending | pending |
| Grant ID | pending | pending | pending |
| Create tx | pending | pending | pending |
| Submit tx(s) | pending | pending | pending |
| Evaluate tx(s) | pending | pending | pending |
| Primary manifests | pending | pending | pending |
| Challenge tx / bond | not required | pending | if exercised |
| Resolve tx / status | not required | pending | if exercised |
| Finalise / activate tx(s) | pending | pending | pending |
| Claim/refund tx(s) | pending | pending | pending |
| Native GEN transfer deltas | pending | pending | pending |
| Before/after accounting | pending | pending | pending |
| Vercel readback | pending | pending | pending |

Never invent any field, hash, validator result or release status. A documented negative result is better than a fabricated successful result.
