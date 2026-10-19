# CLARITY

> Capital that follows verified progress.

**Clarity** is a GenLayer-native, dependency-aware grant escrow. A sponsor funds 2–8 ordered tasks, each with its own immutable recipient, allocation, public evidence authorities and prerequisites. GenLayer validators independently retrieve the frozen evidence and agree on a bounded semantic classification; deterministic contract code determines claimability, bonded disputes and exact native GEN transfers.

**Current status: locally validated, NOT DEPLOYED OR LIVE-VERIFIED.** The contract must not be deployed yet: outgoing native child-transfer failure has no supported recovery path in the pinned runtime, and the clean frontend production checks could not run because package registry access stalled. Do not use any address from other projects. See `docs/RELEASE_GATES.md` and `docs/LIVE_VERIFICATION.md`.

## What Clarity does

- One principal GenLayer Intelligent Contract, chain ID **61999**, RPC `https://studio.genlayer.com/api`.
- No backend, indexer, database, SIWE, off-chain signers, relayers, external auth or second chain.
- Native testnet GEN escrow; **not USDC**, not mainnet funds.
- One payable grant creation: sponsor fixes 2–8 tasks, recipients, bps, source authority, challenge sources, deadlines and prerequisite edges.
- Directed graph is *topologically ordered*: each task may depend only on earlier tasks. No cyclic or forward references.
- Exactly **10,000 bps** funded and allocated; rounding dust belongs to the last task at creation.
- Every task has 2–3 independent public HTTPS sources, at least one required PRIMARY and one required CORROBORATING; optional 0–2 distinct pre-authorised CHALLENGE sources.
- Every validator independently renders the sources and classifies `SATISFIED`, `VIOLATED` or `INCONCLUSIVE`. Incomplete/invalid output remains non-payable.
- Custom GenLayer `run_nondet_unsafe` compares an identical **scalar token + primary source digest + combined source digest**. No dict-vs-string comparison or consensus on arbitrary reasoning prose.
- Challenge: issuer-side sponsor may challenge a SATISFIED result; recipient may challenge a VIOLATED result. Exact 5% task-allocation bond, subsequent independent re-review, deterministic forfeiture/return.
- A satisfied node becomes READY only if **all prerequisites are READY or CLAIMED**; claim moves native GEN strictly to the frozen recipient.
- Unverified, rejected, expired and stalled states have constrained reclaim or refund paths; no arbitrary sponsor seizure of a READY or CLAIMED task.
- Deterministic accounting: `total = remaining + paid + refunded`, and bond ledger `received = locked + returned + forfeited`.

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

The current host passed 76 Python tests (55 offline and 21 GenLayer Direct Mode), 11 frontend protocol tests, GenVM lint, pinned SDK semantic validation and schema extraction. The Pyright check could not write its cache outside the workspace; `npm ci` and `npm ping` stalled, so TypeScript, ESLint and the production build remain unverified. Direct Mode does not prove network consensus or child-transfer delivery. Exact evidence and blockers are recorded in `docs/RELEASE_GATES.md`.

## Deploying (agent-owned, never simulated)

Do not deploy until `docs/RELEASE_GATES.md` is satisfied. In particular, resolve the outgoing transfer failure path and pass clean frontend production checks. On a genuine finalized StudioNet deployment, set **`NEXT_PUBLIC_CLARITY_CONTRACT`** in Vercel to the actual deployed address and rebuild. Reads are deliberately empty/disabled before configuration; no locally invented records appear in the public UI.

## Comparison / originality

- **Not Covenant Watch:** no loans, cross-chain attestation, interest penalties or collateral seizure.
- **Not Redeem:** no single issuer/beneficiary liability or insurance-style guarantee; different task recipients are paid through a dependency graph.
- **Not Stargaze:** no software vulnerability applicability gate or release-security badge; grants are the economic unit.

## Trust boundary

No issuer or admin supplies a validator verdict or a payout amount. Public evidence is an external trust input; multiple URLs do not prove legal publisher independence, semantic truth or immutable byte history. A content digest means only that validators independently observed the same bounded text. If evidence changes during a challenge, Clarity returns inconclusive rather than granting payment. See `docs/SECURITY.md`.

MIT licence for project-authored source. Third-party packages retain their own licences.
