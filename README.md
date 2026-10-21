# CLARITY

> Capital that follows verified progress.

**Clarity** is a GenLayer-native, dependency-aware grant escrow. A sponsor funds 2–8 ordered tasks, each with its own immutable recipient, allocation, public evidence authorities and prerequisites. GenLayer validators independently retrieve the frozen evidence and agree on a bounded semantic classification; deterministic contract code determines claimability, bonded disputes and exact native GEN transfers.

**The recovery revision is deployed on StudioNet at `0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F`.** Its remote schema passes; the two test recipients are registered, but no grant has yet been created on this revision. The previous full lifecycle belongs to the earlier deployment and has not been repeated here. The local frontend checks pass; the accessible browser session has no injected wallet, so its payable grant cannot be submitted yet. Two live failed-child tests produced no callback recovery credit. This is explicitly accepted as a residual limitation; general outgoing-transfer recovery is unproven, including for registered EOAs. Vercel has not been updated; the owner will deploy the frontend. Earlier disposable deployments retain 0.20 GEN without a recovery method and cannot be patched in place. See `docs/DEPLOYMENT.md`, `docs/RELEASE_GATES.md` and `docs/LIVE_VERIFICATION.md`.

## What Clarity does

- One principal GenLayer Intelligent Contract, chain ID **61999**, RPC `https://studio.genlayer.com/api`.
- No backend, indexer, database, SIWE, off-chain signers, relayers, external auth or second chain.
- Native testnet GEN escrow; **not USDC**, not mainnet funds.
- One payable grant creation: sponsor fixes 2–8 tasks, recipients, bps, source authority, challenge sources, deadlines and prerequisite edges.
- Directed graph is *topologically ordered*: each task may depend only on earlier tasks. No cyclic or forward references.
- Exactly **10,000 bps** funded and allocated; rounding dust belongs to the last task at creation.
- Every task has 2–3 independent public HTTPS sources, at least one required PRIMARY and one required CORROBORATING; optional 0–2 distinct pre-authorised CHALLENGE sources.
- Every validator independently renders complete sources up to 2,200 characters each and classifies `SATISFIED`, `VIOLATED` or `INCONCLUSIVE`. Larger rendered sources fail closed; no evidence is silently cut off at a character boundary.
- A provisional decision stores the exact public primary evidence snapshot in its manifest. Challenges re-evaluate that snapshot, so a later publisher edit cannot replace the evidence that supported the original result.
- Custom GenLayer `run_nondet_unsafe` compares an identical evidence-bearing JSON result with the classification and primary/combined source digests. No consensus on arbitrary reasoning prose.
- Challenge: issuer-side sponsor may challenge a SATISFIED result; recipient may challenge a VIOLATED result. Exact 5% task-allocation bond and deterministic forfeiture/return. Challenge URLs are closed at funding; a challenger may submit a rationale but cannot add URLs. If resolution stalls, the original provisional result is finalized and the bond becomes a pull credit.
- Expected grant-validation errors and unknown-selector calls record incoming GEN as a recovery credit owned by the original EOA. The contract implements a GenVM errored-message callback, but two controlled failed children on StudioNet produced no recovery credit. This limitation is explicitly accepted for the current release; do not rely on or claim general outgoing-transfer recovery. Bond outcomes are pull credits. Fatal VM/ABI failures before dispatch and empty-calldata transfers without a supported receive handler remain outside the funding-recovery protection.
- A recipient must register from its own direct EOA wallet before the sponsor can fund a grant; contract wallets are rejected so recipient code cannot revert the native transfer. A satisfied node becomes READY only if **all prerequisites are READY or CLAIMED**; only the frozen recipient may initiate the claim transfer.
- Unverified, rejected, expired and stalled states have constrained reclaim or refund paths; no arbitrary sponsor seizure of a READY or CLAIMED task.
- A `SATISFIED_BLOCKED` allocation is refundable after the grace period only when a prerequisite is still not `READY` or `CLAIMED`. If a blocked allocation is refunded before a late prerequisite completes, the refund is final.
- Deterministic escrow accounting: `total = remaining + paid + refunded`, separate from recoverable failed-funding credits. Bond ledger: `received = locked + returned + forfeited`.

## Repo structure

```text
contracts/clarity.py          GenLayer Intelligent Contract (escrow, consensus, graph, challenges)
frontend/                     Next.js 15 / TypeScript / injected EIP-1193 frontend
frontend/src/lib/protocol.mjs  Pure wei arithmetic, lifecycle status and graph validation
frontend/test/                Pure frontend protocol regression tests
tests/                        Offline state-model harness (not real GenVM)
scripts/                      Source parity / read-only StudioNet verification helpers
docs/                         Architecture, threat model, release gates and reviewer matrix
.github/workflows/ci.yml      Source + offline tests + frontend build gate
```

## Local verification

```bash
python -m pytest -p gltest.direct.pytest_plugin -p gltest.fixtures -q
python -m py_compile contracts/clarity.py
node --test frontend/test/*.test.mjs
npm ci --prefix frontend
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

Local tests and build status for this recovery revision are recorded in `docs/RELEASE_GATES.md`. The previous deployed source address predates the added recovery callback and pull-credit methods, and must not be paired with the updated frontend. Live child-transfer failure recovery still requires a controlled test before it can be described as proven.

## Deployment boundary

The local environment file points to the recovery deployment. Set `NEXT_PUBLIC_CLARITY_CONTRACT=0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F` in Vercel when deploying the frontend; the owner will perform that deployment after reviewing the callback limitation.

## Comparison / originality

- **Not Covenant Watch:** no loans, cross-chain attestation, interest penalties or collateral seizure.
- **Not Redeem:** no single issuer/beneficiary liability or insurance-style guarantee; different task recipients are paid through a dependency graph.
- **Not Stargaze:** no software vulnerability applicability gate or release-security badge; grants are the economic unit.

## Trust boundary

No issuer or admin supplies a validator verdict or a payout amount. Public evidence is an external trust input; multiple URLs do not prove legal publisher independence or semantic truth. A content digest means only that validators independently observed the same bounded text. A challenge reuses the provisional primary-evidence snapshot; if additional challenge evidence is unavailable or cannot resolve, recovery finalizes the original provisional result. See `docs/SECURITY.md`.

MIT licence for project-authored source. Third-party packages retain their own licences.
