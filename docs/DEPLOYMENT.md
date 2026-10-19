# Deployment runbook / blank evidence record

**Status:** Canonical deployment and live read verification complete. The Vercel project variable is set locally; the owner will perform the Vercel deployment.

Network `studionet`, chain ID `61999`, RPC `https://studio.genlayer.com/api`, explorer `https://explorer-studio.genlayer.com`, repo-local CLI `genlayer@0.39.1`.

1. Repo-local CLI 0.39.1, GenVM linter 0.11.0 and Direct Mode `genlayer-test==0.29.2` were used. GenVM AST checks, pinned SDK validation/typecheck and schema generation passed. Full local suite: 81 tests; frontend protocol suite: 11 tests.
2. Frontend TypeScript, ESLint, protocol tests and production build passed in an isolated install with the canonical address configured.
3. The canonical contract was deployed from `contracts/clarity.py` to chain **61999** using the already-unlocked sponsor wallet. Sponsors and beneficiaries must be direct EOAs; each beneficiary registered before funding.
4. Canonical fresh reads returned grant count 0 and all-zero accounting before live scenarios. Live grant/task reads and final accounting are recorded in `docs/LIVE_VERIFICATION.md`.
5. For Vercel, set `NEXT_PUBLIC_CLARITY_CONTRACT=0x449f08f7407559D3e7538979B666D08ec35536B8` and deploy the `frontend` directory manually.
6. After deployment, verify the public read page, injected-wallet connect/disconnect, wrong-chain behavior and real writes against this address. The final public URL is not yet available.

## Final immutable deployment record (to complete after actual deployment)

```text
Git commit: `ca80a3ddca5349d6bae0ddbbe52b3e8a1ebb927b` (release implementation)
Source SHA-256: `2da5ab7c7175a85facced4394d9a5762b6136e9597625682e7e6939d17c52eb59`
Contract: `0x449f08f7407559D3e7538979B666D08ec35536B8`
Deployment transaction: `0xb51c7ff6d203fbdf318f986358bcf9b85dd634f3c1b1257b6c5498809815748c`
Consensus: `FINALIZED`, `MAJORITY_AGREE`
Execution: `SUCCESS`
Network: StudioNet, chain ID 61999
Production frontend: owner’s Vercel deployment pending
Final CI run: [39301675436](https://github.com/Ifem1/Clarity/actions/runs/39301675436), all three jobs passed

Deployment is protected against recipient-controlled transfer reverts: sponsor and recipient addresses must be EOAs, and task beneficiaries self-register before funding. Scenario A verified actual GEN delivery on StudioNet. Two failed disposable test deployments hold 0.10 GEN each without app accounting after unsuccessful payable calls; see the incident record in `docs/LIVE_VERIFICATION.md`.
```
