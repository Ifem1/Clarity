# CLARITY

> Capital that follows verified progress.

**Clarity** is a GenLayer-native, dependency-aware grant escrow. A sponsor funds 2–8 ordered tasks, each with its own immutable recipient, allocation, public evidence authorities and prerequisites. GenLayer validators independently retrieve the frozen evidence and agree on a bounded semantic classification; deterministic contract code determines claimability, bonded disputes and exact native GEN transfers.

**Current status: canonical StudioNet deployment and native live lifecycle proofs recorded; final source push and Vercel deployment remain.** The canonical contract is `0x449f08f7407559D3e7538979B666D08ec35536B8` on chain 61999. Sponsors and beneficiaries submit directly from EOAs; beneficiaries register on this contract before a grant is funded. See `docs/DEPLOYMENT.md`, `docs/RELEASE_GATES.md` and `docs/LIVE_VERIFICATION.md` for hashes, receipts and live accounting.

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
- A recipient must register from its own direct EOA wallet before the sponsor can fund a grant; contract wallets are rejected so recipient code cannot revert the native transfer. A satisfied node becomes READY only if **all prerequisites are READY or CLAIMED**; claim moves native GEN strictly to the frozen recipient.
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

The current host passed 81 Python tests (57 offline and 24 GenLayer Direct Mode), 11 frontend protocol tests, TypeScript, ESLint, production build, GenVM lint, pinned SDK semantic validation/typecheck and schema extraction. Three live StudioNet scenarios exercised dependency payout, a challenged VIOLATED result with bond forfeiture/refund, and fail-closed no-majority recovery. Exact evidence and remaining release gates are recorded in `docs/RELEASE_GATES.md`.

## Deploying (agent-owned, never simulated)

The canonical contract is deployed and locally configured in `frontend/.env.local` as `NEXT_PUBLIC_CLARITY_CONTRACT=0x449f08f7407559D3e7538979B666D08ec35536B8`. For the owner’s manual Vercel deployment, set that same variable in the Vercel project and build from `frontend/`. Reads are deliberately empty/disabled when no address is configured; no locally invented records appear in the public UI.

## Comparison / originality

- **Not Covenant Watch:** no loans, cross-chain attestation, interest penalties or collateral seizure.
- **Not Redeem:** no single issuer/beneficiary liability or insurance-style guarantee; different task recipients are paid through a dependency graph.
- **Not Stargaze:** no software vulnerability applicability gate or release-security badge; grants are the economic unit.

## Trust boundary

No issuer or admin supplies a validator verdict or a payout amount. Public evidence is an external trust input; multiple URLs do not prove legal publisher independence, semantic truth or immutable byte history. A content digest means only that validators independently observed the same bounded text. If evidence changes during a challenge, Clarity returns inconclusive rather than granting payment. See `docs/SECURITY.md`.

MIT licence for project-authored source. Third-party packages retain their own licences.
