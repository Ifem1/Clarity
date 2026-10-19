# Live contract verification

**Canonical deployment:** [`0x449f08f7407559D3e7538979B666D08ec35536B8`](https://explorer-studio.genlayer.com/address/0x449f08f7407559D3e7538979B666D08ec35536B8), StudioNet chain 61999. All transactions below were sent to this contract unless explicitly identified as abandoned test deployments. A transaction counts as successful only when finalized and its GenVM execution result is `SUCCESS`.

## Local validation (not live-chain evidence)

- Offline state model: 57 passed. GenLayer Direct Mode: 24 passed. Combined: 81 passed.
- Frontend protocol tests: 11 passed. TypeScript, ESLint and optimized Next build passed in the isolated frontend install configured with the canonical address.
- GenVM linter AST checks, SDK semantic validation, schema extraction and pinned-runner Pyright typecheck passed. Schema: 18 methods (7 views, 11 writes).
- Direct Mode records native transfer intents but does not execute child messages or prove live recipient balance changes. Scenario A below provides that live proof for an EOA recipient.

## Initial canonical deployment

```text
Contract: 0x449f08f7407559D3e7538979B666D08ec35536B8
Deploy tx: 0xb51c7ff6d203fbdf318f986358bcf9b85dd634f3c1b1257b6c5498809815748c
Receipt: FINALIZED / MAJORITY_AGREE / leader GenVM SUCCESS
Source SHA-256: 2da5ab7c7175a85facced4394d9a5762b6136e9597625682e7e6939d17c52eb59
Network: StudioNet, chain ID 61999
Initial reads: get_grant_count() = 0; all escrow and bond accounting = 0
```

Recipients self-registered on the canonical instance before funding:

- `pore-test` (`0xc77170b966f232473da92655e670f2e277cac5a9`): `0xead8f952cfb6edd9af17e8f76d9b3d36bea8709573365ae4260e47599bf097f5`
- `chronicle-test-wallet` (`0x6b476bf35c4968f3f1775c0ca2110591b4b5fcbe`): `0xf733f16c087b1a724ad690d31d4d42d20ad2009a656debdf85a6c857d0f732cc`

Both `is_registered_recipient(address)` reads returned true on the canonical contract.

## Scenario A — successful dependency disbursement

Grant 1 escrowed exactly 0.10 GEN with 40%/60% task allocations and a 300-second challenge window. NASA’s Apollo 11 page and the Smithsonian National Air and Space Museum’s timeline were independently fetched for each assessment: [NASA mission record](https://www.nasa.gov/mission/apollo-11/) and [Smithsonian timeline](https://airandspace.si.edu/explore/stories/apollo-missions/apollo-11-moon-landing/apollo-11-timeline).

| Operation | Finalized tx | Result |
|---|---|---|
| Create grant 1 (0.10 GEN) | `0x3c4ab5e10c9d1056fc445f2029861e26bc7186cb869deae78628b6f65f6131b2` | `SUCCESS`, `MAJORITY_AGREE` |
| Submit task 0 (`pore-test`) | `0xb771082f71568e946df33ba77ec7c67feb17d99ae23ba76330f5f5c38ba71388` | `SUCCESS`, `MAJORITY_AGREE` |
| Submit task 1 (`chronicle-test-wallet`) | `0xfbbb0cb6f87b9c321f4783a53e81cee04c8a97c5605c3afab16839cefc54414c` | `SUCCESS`, `MAJORITY_AGREE` |
| Evaluate task 0 | `0xb748837092672a7a3ee288d7add6e1d0c27046b81d4e9ca79793c233be42a396` | `SUCCESS`, `MAJORITY_AGREE`, one dissent |
| Evaluate task 1 (first try) | `0x7675fed55ee7e8765bafebee4c4dc27a862e80b61bb8ad3e491d2d6e3afb8428` | `MAJORITY_DISAGREE`; no task attempt or manifest committed |
| Evaluate task 1 (second try) | `0xb39deb9cd69949ef9976c28def9116630632bd89981c6416fb30ffac3c29e29d` | `MAJORITY_DISAGREE`; no task attempt or manifest committed |
| Evaluate task 1 (retry) | `0x41c69e339273fb5ea809b0d42f6081d1b12985e73dd82ecb68ab864685a7ef80` | `SUCCESS`, `MAJORITY_AGREE`, two dissenting votes |
| Finalize task 1 before task 0 | `0xd35f916c8f6204fe3d0d9fd49b2ca57caabbe4f849d32febe3f01ccf641bf64d` | `SUCCESS`; task 1 stored as `SATISFIED_BLOCKED` (status 5) |
| Finalize task 0 | `0x8276920883da1bf45c61ed0a6ae1c7dac54dc2cc666299fa9c86e79cb564ac5e` | `SUCCESS`; task 0 became `READY` (status 6) |
| Activate task 1 | `0x19501fe8b1987309ffb0144669c4226cdf9a76aa939dd8d04340084ea19b7eae` | `SUCCESS`; task 1 became `READY` |
| Claim task 0 | `0x0f3b43edef60b1aa58b1227f49c8e863383032997ef5833f56ca142954d563e4` | `SUCCESS`; 0.04 GEN transfer finalized |
| Claim task 1 | `0xc35e8294154d898f2c1a8d43cae2789c213f1d7c9a271654cb0a11fb823b515e` | `SUCCESS`; 0.06 GEN transfer finalized |

The primary source digests were `e923e364a3c5e9c1b851f2deb1d6e22bfbeb99943a800119b6f379944c171ed3` (task 0) and `3ba98ba79b552ff57f61e0dcd73e377b7913b4d1b7eb6d600e78b7eb02df691e` (task 1). Both primary manifests recorded `SATISFIED` with two required sources.

Balance evidence (wei):

| Address | Before claims | After claims | Delta |
|---|---:|---:|---:|
| `pore-test` | 9,199,999,999,999,999,799 | 9,239,999,999,999,999,799 | +40,000,000,000,000,000 (0.04 GEN) |
| `chronicle-test-wallet` | 996,949,000,000,000,000,010 | 997,009,000,000,000,000,010 | +60,000,000,000,000,000 (0.06 GEN) |
| Canonical contract | 100,000,000,000,000,000 | 0 | -0.10 GEN |

Grant 1 accounting after settlement: funded 0.10 GEN = paid 0.10 GEN + refunded 0 + remaining 0. No challenge bonds were used.

## Scenario B — rejected payout, bonded challenge and refund

Grant 2 escrowed 0.10 GEN. Task 0 required the false statement “Apollo 11 launched on July 17, 1969”; both frozen sources give July 16. The source digest was `3ba98ba79b552ff57f61e0dcd73e377b7913b4d1b7eb6d600e78b7eb02df691e`.

| Operation | Transaction | Result |
|---|---|---|
| Create grant 2 (0.10 GEN) | `0x23c1a9494e8a3e1b48db977b62f985df218931095bf203ba3ff02dd9e349ba34` | `SUCCESS`, `MAJORITY_AGREE` |
| Submit task 0 | `0x509ff087578929b65b6e81a0bb185342a60a63f91cbafcfe757b2d1b88415562` | `SUCCESS`, `MAJORITY_AGREE` |
| Evaluate task 0 (initial attempt) | `0x7951e025d3184aaab39cf54918a79a99d37395377c2ff084cc20106eb8ea83ef` | `CANCELED`, `NO_MAJORITY`, zero validators; no state change |
| Evaluate task 0 (retry) | `0x71def8be5f82670934d8f1922bc66bce7c6c37123e3c4cc5b76092b07731585e` | `FINALIZED`, `SUCCESS`, `MAJORITY_AGREE` |
| Challenge with exact 0.002 GEN bond | `0x459cc13dcc6e32031ec5a58ca0cd96109da7ba8274a28f6f390911a07a85cc3d` | `SUCCESS`; recipient challenged task allocation 0.04 GEN |
| Resolve challenge independently | `0xe0344413838599cc0cd36cfe82f751341582e129dfef87280245b1b579666e5f` | `FINALIZED`, `MAJORITY_AGREE`; challenge manifest `VIOLATED` |
| Refund rejected 0.04 GEN | `0x4e7ff306b1f72a8e66c9d37035004255d60c19aec0738b3e91629a212af5e1f9` | `SUCCESS`; task 0 `REFUNDED`, beneficiary paid 0 |

Bond accounting after resolution: received 0.002 GEN = forfeited to sponsor 0.002 GEN; locked 0; returned 0. The sponsor’s balance rose by exactly the forfeited 0.002 GEN, and the recipient’s challenge stake decreased by 0.002 GEN. The rejected allocation refund returned 0.04 GEN to the sponsor. Task 1 then independently passed its July 24 splashdown assessment and its 0.06 GEN allocation was settled:

- Submit task 1: `0x0b05e4cb8639d0aeba6f0be211029200a914e55a3f5919c305321b6e068149d0` (`SUCCESS`).
- Evaluate task 1: `0x190198cafe2bb1ba71a9d13b1753424d35a3558805125d4f395f533ba0a0ef31` (`FINALIZED`, `SUCCESS`, `MAJORITY_AGREE`; two dissenting votes); source digest `e923e364a3c5e9c1b851f2deb1d6e22bfbeb99943a800119b6f379944c171ed3`.
- Finalize task 1: `0x2a68ac950f5f09e3042258d1327b9ead9959b6c3c6d7759fe609f8b19ccaafc9` (`FINALIZED`, `SUCCESS`). Claim 0.06 GEN: `0x843c4798ac203d6e98bf835808d28fb056f1827c0da656a82e49ba5d938d5af0` (`FINALIZED`, `SUCCESS`).

## Scenario C — live disagreement, no-majority cancellation and retry

The first two task 1 evaluations in grant 1 ended in `MAJORITY_DISAGREE`. Reads immediately afterward showed `SUBMITTED`, attempts 0, no provisional label and no manifest. A third evaluation succeeded and the normal finalization path completed. For grant 2, evaluation `0x7951…a83ef` had `NO_MAJORITY`, `CANCELED`, no validators and `value_credited: false`; task 0 remained `SUBMITTED`, attempts 0. Retry `0x71def…1585e` later finalized with a `VIOLATED` manifest. These genuine chain results show disagreement/no-majority did not release or settle funds and recovery by a later evaluation was possible.

## Closing canonical ledger

Final readback after grant 2 task 1 is finalized and claimed:

```text
Global escrow: funded 0.20 GEN = paid 0.16 GEN + refunded 0.04 GEN + remaining 0
Bond ledger: received 0.002 GEN = locked 0 + returned 0 + forfeited 0.002 GEN
Canonical contract native balance: 0
Grant 1: funded 0.10, paid 0.10, refunded 0, remaining 0
Grant 2: funded 0.10, paid 0.06, refunded 0.04, remaining 0
Final sponsor balance: 967493289999999999984 wei
Final pore-test balance: 9237999999999999799 wei
Final chronicle-test-wallet balance: 997069000000000000010 wei
```

## Local front-end wallet transaction smoke test

Using the already-unlocked Chrome wallet connected to the local production build, the wallet owner approved one `register_recipient()` transaction from `0xd6423ae82a975d55c6ceac222827a727325e0459` to the canonical contract. No GEN value was attached and no grant was created or funded.

```text
Transaction: 0x207c8947e943045f531bdf572303f8a63e54d43c74d6d1c0be27381a5250c2e0
Receipt: FINALIZED / MAJORITY_AGREE / GenVM SUCCESS
value_credited: false
Follow-up is_registered_recipient(sender): true
```

The transaction finalized on chain, but the original front-end receipt waiter timed out while treating the SDK's raw `ACCEPTED` status as finality state. The app was corrected to poll the SDK's normalized transaction record, which exposes the finalized status and execution result. The local production build then reconnected the wallet and displayed it as registered. No second transaction was sent.

## Abandoned test deployment incident

Two disposable deployments are not canonical. Each received a failed payable `create_grant` transaction whose receipt reports `value_credited: true` while GenVM execution failed and the application ledger rolled back. Their native balances were read as 0.10 GEN each, with `get_grant_count() == 0` and zero accounting. The first failure (`0x470c3adc63b3a974d966bc182a4f56b95744531ff154c49ab6811a9387e2c1eb`) was caused by a local test helper serializing the deadline as a string. The second (`0xb2e317afb8b0095743b638e7b4d7294f544d9edc10e524b254004a0a21c790ed`) used recipients not registered on that specific contract instance. Their addresses are `0x3843E1D7E9f6748DB2ff99B3cdc55E9Cde3cBe1D` and `0x22E01FAE9D2032926bcE4399AFaB4bB29fAf93f8`; neither is configured in the frontend. The contract ABI has no recovery method, so those 0.20 testnet GEN are stranded. The canonical contract was deployed separately, input checks were corrected, both recipients were registered on that instance before funding, and all canonical escrow settled as recorded above.

## Remaining external release checks

- Push the final source/evidence commit to `https://github.com/Ifem1/Clarity.git` and record the CI run.
- The owner deploys the frontend to Vercel using `NEXT_PUBLIC_CLARITY_CONTRACT=0x449f08f7407559D3e7538979B666D08ec35536B8`.
- Verify injected-wallet behavior and public production reads after the Vercel URL exists.

No receipt, digest, balance or validator result in this file is simulated. Failed transactions are retained as failures, not counted as successful scenarios.
