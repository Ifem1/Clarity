# Deployment runbook / blank evidence record

**Status:** Recovery source is deployed on StudioNet at `0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F`. The live failed-child callback did not credit either probe ledger, so outgoing-transfer recovery remains unproven. Vercel deployment remains the owner's action.

Network `studionet`, chain ID `61999`, RPC `https://studio.genlayer.com/api`, explorer `https://explorer-studio.genlayer.com`, repo-local CLI `genlayer@0.39.1`.

1. Repo-local CLI 0.39.1, GenVM linter 0.11.0 and Direct Mode `genlayer-test==0.29.2` are pinned. GenVM validation and remote schema read pass with the contract-level schema compatibility override.
2. The current recovery deployment adds failed-funding recovery, failed-transfer credit, and bond pull-credit methods. Its remote schema contains 24 public methods.
3. The canonical contract was deployed from `contracts/clarity.py` to chain **61999** using the already-unlocked sponsor wallet. Sponsors and beneficiaries must be direct EOAs; each beneficiary registered before funding.
4. Canonical fresh reads returned grant count 0 and all-zero accounting before live scenarios. Live grant/task reads and final accounting are recorded in `docs/LIVE_VERIFICATION.md`.
5. Previous corrected deployment is `0x41428Aa8357fF8cC867b0fc98133E54d430510d0`. The recovery revision uses `0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F`; see `LIVE_VERIFICATION.md`.
6. Local `.env.local` now uses the recovery address. Vercel remains with the owner.

## Historical deployment record

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

The 0.20 GEN historical disposable deployment losses cannot be recovered by this revision: those contracts are immutable and have no corresponding recovery selector. See the incident record in `docs/LIVE_VERIFICATION.md`.
```

## Corrected source deployment record

```text
Status: deployed, source-matched; recovery, evidence snapshot, challenge, first payout and rejected-task refund verified; dependent payout awaits challenge-window expiry
Current source SHA-256: `75405b4ae80e75be12958c4caad422f1af02312884d28b4b8f98c69e6dda23c2`
Deployment tx: `0xaf53b63c8d34e0a6f55756aee9ef0166d252d608a8d7f2281001b1faf414f0c8`
Contract: `0x41428Aa8357fF8cC867b0fc98133E54d430510d0`
Receipt: `FINALIZED / MAJORITY_AGREE / SUCCESS`
Frontend contract configuration: `NEXT_PUBLIC_CLARITY_CONTRACT=0x41428Aa8357fF8cC867b0fc98133E54d430510d0`
Vercel production deployment: owner will perform after reviewing this package
```

## Recovery revision deployment record

```text
Contract: 0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F
Deploy transaction: 0x55f92c4920c2e8f7bd94e6be3c0ccedaacaf22ea46af25a52dc8aba6090f82c8
Receipt status ACCEPTED / MAJORITY_AGREE / leader GenVM SUCCESS; remote schema and fresh reads succeed
Network: StudioNet, chain ID 61999
Source SHA-256: FA0378E65C8E1DB32E3E93DD0ED910311B5433BCF9D754E4F54B323DA9B2AB1E
Remote schema: 24 methods; schema query succeeds
Fresh reads: grant count 0; all accounting fields 0
Frontend contract: NEXT_PUBLIC_CLARITY_CONTRACT=0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F
```

The first recovery deployment (`0x71093Fd7558988E295cc01f5651ad792DA6a5120`) was accepted but its remote schema call failed because the runtime schema generator exposed protocol handlers as public ABI methods. The deployed source was corrected to supply a filtered schema; the recovery deployment above returns its schema successfully. A live controlled failed child call is recorded in `LIVE_VERIFICATION.md` and did not produce a callback credit.
