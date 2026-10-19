# Live contract verification

**NOT EXECUTED / no real deployment.** No transactions, contract address, manifests or live claims are recorded here.

## Local test evidence (not live chain evidence)

- Full local suite: 76 passed (55 offline state-model + 21 GenLayer Direct Mode).
- GenLayer Direct Mode public-method suite: 21 passed using installed `genlayer-test==0.29.2` with the source-pinned GenLayer SDK dependency.
- Direct Mode observed exact `EthSend` native transfer requests for claims, refunds and bonds, including recipient, value and finalized setting. The fixture does not execute child transfers or model a recipient's receive handler, so this does not prove balance deltas, atomic rollback or recovery after transfer failure.
- A Direct Mode injected `EthSend` failure raises at the child-message hook after the contract has updated the parent task ledger. The test environment has no transaction-level storage rollback, so the observed residual ledger is a harness limitation and cannot establish actual chain behavior. Live GenVM failure atomicity is an essential unresolved gate.
- Frontend protocol utility suite: 11 passed. Clean `npm ci` stalled in an isolated temporary folder, and `npm ping` did not return. Existing partial dependencies lack `tsc`, `next`, and `next/core-web-vitals`, so typecheck, lint and production build remain unverified.
- GenVM linter AST checks (3), pinned SDK semantic validation (16 methods; 6 views, 10 writes), Python syntax compile, and schema extraction passed. The Pyright typecheck is blocked because its installed CLI writes to the protected `C:\Users\DELL\.cache\genvm-linter` path.
- Transfer failure review: the pinned GenVM SDK documents `__on_errored_message__` for handling failed incoming value transfers. It does not expose an equivalent callback for failed outgoing child transfers. Clarity commits claim/refund/bond accounting before emitting the finalized native transfer. If that child fails, the contract has no supported automatic recovery path; this is a release blocker.
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
