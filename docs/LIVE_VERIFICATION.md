# Live contract verification

> **Historical lifecycle deployment:** corrected source SHA-256 `75405b4ae80e75be12958c4caad422f1af02312884b4b8f98c69e6dda23c2` at `0x41428Aa8357fF8cC867b0fc98133E54d430510d0` is the address used for the lifecycle scenarios below. The current recovery revision is `0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F`; its schema and initial state are recorded later. Only finalized state changes are counted.

**Canonical deployment:** [`0x449f08f7407559D3e7538979B666D08ec35536B8`](https://explorer-studio.genlayer.com/address/0x449f08f7407559D3e7538979B666D08ec35536B8), StudioNet chain 61999. All transactions below were sent to this contract unless explicitly identified as abandoned test deployments. A transaction counts as successful only when finalized and its GenVM execution result is `SUCCESS`.

## Local validation (not live-chain evidence)

- Current recovery checkout: 57 offline tests and 32 GenLayer Direct Mode tests passed; frontend protocol tests 13/13, TypeScript, ESLint, optimized Next build, AST lint and Pyright passed.
- An earlier source revision passed GenVM lint, SDK semantic validation and schema extraction with 20 methods. The recovery revision passes GenVM validation and its 24-method schema is recorded in `evidence/contract-schema.json`; the deployed contract also returns that schema remotely.
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

## Corrected source deployment and live checks

```text
Contract: 0x41428Aa8357fF8cC867b0fc98133E54d430510d0
Deploy tx: 0xaf53b63c8d34e0a6f55756aee9ef0166d252d608a8d7f2281001b1faf414f0c8
Receipt: FINALIZED / MAJORITY_AGREE / leader GenVM SUCCESS
Source SHA-256: 75405b4ae80e75be12958c4caad422f1af02312884b4b8f98c69e6dda23c2
Network: StudioNet, chain ID 61999
Schema: includes get_funding_recovery, recover_failed_funding, and evidence_json manifests
Source parity: getContractCode SHA-256 matched local source
Frontend local contract: NEXT_PUBLIC_CLARITY_CONTRACT points to this address
```

The contract was initially empty. Both already-unlocked recipients registered successfully: `pore-test` (`0xc77170b966f232473da92655e670f2e277cac5a9`, tx `0x2cec7bef67f2c7562db8402cdfc8ce9368fa538bf24c14195f6ba07660241c1e`) and `chronicle-test-wallet` (`0x6b476bf35c4968f3f1775c0ca2110591b4b5fcbe`, tx `0x11ada17474c033cd39cf190f34f70a0d68983c564b3a6bd3141ada5c1a1b0932`).

The corrected payable validation failure path was exercised with one wei. Invalid grant creation produced no grant and credited one wei to the sending sponsor's recovery balance (`0x355ed4835fc0ca2fe9e6ab66f0d0a0fadd82b5d394c9ce3e770b07ba4e1f1c5e`); the origin recovered that wei (`0xbc8e17de5be7ae5c6767d65860b6b7ba0786be7949906cd3d148b2eaf9378373`). A second validation failure from duplicate registrable source domains also recovered 0.04 GEN (`0xe3fa881a79623b6f1eded8d88247b3aa82f27b439f16aceb77832acea2551a61`).

Three early full-size scenarios were funded before evidence snapshots exposed the live source-size issue: grant 1 holds 0.10 GEN, grant 2 holds 0.04 GEN, and grant 3 holds 0.04 GEN. Grant 1 task evaluations finalized as transactions but returned `SOURCE_TOO_LARGE`; task 3 task 1 did likewise. These allocations remain unsettled and are refundable only after each grant's deadline plus the seven-day review grace. Grant 2 has submitted tasks but no evaluation. Do not count these as completed payouts.

Grant 4 is the compact-source live lifecycle probe. It escrowed 0.00004 GEN, with 0.00002 / 0.000012 / 0.000008 GEN allocations. All three task submissions finalized. Task 0 evaluated successfully as `SATISFIED` with source digest `81305121f7a16458065fca3c05a0070d6470bd3f1012606e04eed7b455d8f38f`; the stored primary manifest contains the fetched NASA event table and the independent ESA caption, both within size limits. The sponsor challenged with the exact 0.000001 GEN bond (`0xbf6e0d6b6ffe450841da2ec350554c47ba26b4f93aa4072c364b035efb93a2c3`).

Challenge resolution finalized successfully (`0xe07fd67b66468d36d2d0c7ca418a138fe246cb36b72a4b5e8e08f133535281ad`). It classified the frozen challenge snapshot as `SATISFIED`; task 0 became READY and the sponsor's 0.000001 GEN bond was forfeited under the contract outcome. Pore claimed task 0's 0.00002 GEN (`0x613238bbbaf96d91aae64b04927dc18c709ce8250691affdf2716244dad27479`). Task 1 evaluations `0x85e199d6ac97ee0a4f86c7300d57937fceb79df0ff7b0c7dcb18da7f4f1aef97`, `0xe611ec4c63cb7c76420f7fd3211f24039332b107c19e674e831a398aec88ae0`, and `0xe1bf8a242491323d2960e2f75964fc8e0058d6b58d911f007d16bf068aad7156` returned `UNDETERMINED` without state changes. A later attempt finalized successfully (`0x276411ff3135b8951172ff296788874058ff81684bc292b5874a29c9437b05e9`) as provisional `SATISFIED` using the same compact snapshot. After its five-minute challenge period, task 1 finalized (`0x08305b41ba3407a39d1f18c19f16e31a6faeade99509f0f012c6a819d9b9d376`) directly as READY because task 0 was already CLAIMED; its 0.000012 GEN payment finalized to chronicle-test-wallet (`0xee09bc542e54c8054da18a6d0355695395575e1d7883534ec42501e6037d4cf2`).

Task 2 evaluation finalized (`0xf5459ca8272a2f5a1c1523496b710e9b354cf9bd4cce6d373e350a4e65bb2d15`) as provisional `VIOLATED`, with both compact evidence sources recorded and `too_large=false`. After the challenge period, task 2 finalized rejected (`0xa2a2d4517f4b93c034ffc93f14101fffff738a38c69a3c5549823f3b06da4e2f`) and its 0.000008 GEN refund to the sponsor finalized (`0xfe345a6909a98c883aac24b46d7870fc7f5eb9c67274c3f2d4105a14c9ed0c8c`). Final grant 4 accounting is funded 0.00004 GEN = paid 0.000032 + refunded 0.000008 + remaining 0. Global accounting is funded 0.18004 GEN = paid 0.000032 + refunded 0.000008 + remaining 0.18 GEN; bond accounting is received 0.000001 = forfeited 0.000001, locked/returned 0. The remaining 0.18 GEN in grants 1–3 was funded in earlier probes and is not yet refundable until each deadline plus seven-day review grace: grant 1 after 2026-10-28 20:40:55 UTC, grant 2 after 2026-10-28 20:52:36 UTC, and grant 3 after 2026-10-28 20:57:46 UTC.

The local production frontend detail page was refreshed and showed task 0 and task 1 `CLAIMED`, task 2 `REFUNDED`, and zero remaining for grant 4. The registry listed all four live grants. Vercel was not deployed.

Local production frontend at `http://127.0.0.1:3000` was refreshed against the corrected address and successfully rendered the live grant registry, including grants 1–4. Vercel was not deployed.

## Current local safety regression coverage

The current checkout adds Direct Mode and adversarial checks for payable validation failures, origin-owned fallback recovery, simulated failed-child callback credits, owner-only transfer recovery and bond credits, source snapshot integrity, oversized evidence rejection, and dependency-refund ordering. Direct Mode does not execute real child messages or prove chain rollback/callback delivery.

## Recovery revision deployment and failed-child callback probe

```text
Recovery contract: 0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F
Deployment tx: 0x55f92c4920c2e8f7bd94e6be3c0ccedaacaf22ea46af25a52dc8aba6090f82c8
Source SHA-256: fa0378e65c8e1db32e3e93dd0ed910311b5433bcf9d754e4f54b323da9b2ab1e
Network: StudioNet, chain ID 61999
Remote schema: SUCCESS, 24 public methods (10 views, 14 writes)
Initial get_grant_count: 0
Initial accounting: all fields 0
```

On 2026-10-21, the already-unlocked `pore-test` (`0xc77170b966f232473da92655e670f2e277cac5a9`) and `chronicle-test-wallet` (`0x6b476bf35c4968f3f1775c0ca2110591b4b5fcbe`) accounts each registered on this recovery deployment. Transactions were `0x8af1dbe2cc57137264065de03aec55c72714a77ea32b3c2e988bbb1ad3908160` and `0xc741c42ff209e532c4129476e195f2a82ed39c86bef10728d4ee0f2c11ff5f31`; subsequent `is_registered_recipient` reads returned `true` for both. A local frontend payable grant smoke test was later recorded below.

The local production frontend submitted one payable `create_grant` transaction to verify grant creation. The StudioNet explorer lists it as finalized with GenVM SUCCESS; the 0.00004 GEN escrow and transaction are recorded below. This smoke test validates frontend transaction submission only; lifecycle actions for this grant were not run.

### Local frontend payable grant smoke test

```text
Transaction: 0xaae29915208d406cb31b11d4de5136346e644fc1d8e0df565464969cc533516c
Explorer: https://explorer-studio.genlayer.com/tx/0xaae29915208d406cb31b11d4de5136346e644fc1d8e0df565464969cc533516c
Contract: 0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F
Method: create_grant
Status: FINALIZED / GenVM SUCCESS / consensus Accepted
Value: 0.00004 GEN
Frontend: local production build at http://127.0.0.1:3002/new
Purpose: frontend submission smoke test only; scripted lifecycle evidence is separate.
```

The explorer contract page lists this finalized successful call. Its dedicated transaction-detail page returned “Failed to fetch transaction” during verification, so the contract transaction row is the source for the receipt status. This smoke test does not claim to have exercised task review, challenge, payout or refund controls.
Local frontend verification on 2026-10-21: `npm test` passed 13/13 protocol tests; `npm run typecheck`, `npm run lint`, and `npm run build` passed. The local production page at `http://127.0.0.1:3002/` successfully read the recovery contract and displayed its expected empty grant registry. Python tests passed 89/89. The GenVM linter could not load its pinned SDK archive from the local cache during this rerun; deployment-time validation and remote schema extraction for this exact recovery source had succeeded earlier.

The first revision deployment at `0x71093Fd7558988E295cc01f5651ad792DA6a5120` could not return its remote ABI schema because the network SDK included the public protocol handlers `__handle_undefined_method__` and `__on_errored_message__` as ABI methods. The recovery source now overrides `__get_schema__` and filters protocol handlers while retaining the runtime callbacks. The redeployed contract's remote schema query succeeds.

A disposable payable receiver deliberately raised `gl.vm.UserError` from `reject_transfer`. The sender emitted 0.0001 GEN through a finalized internal child message:

```text
Probe parent tx: 0x833ec8a410e7e82afd4cb64941d8231eca876bbc1b82b8a2a22485b3d2d9d823
Failed child tx: 0x564603699bb2706734a3a761633a7535a7042da1b1cb2439e54996f163d235be
Sender probe: 0x0ad93de0b2492380aD997Ad215e6C3Faee4a20CF
Receiver: 0xb3941AaD8a4AcA807b732225c568F510B1A5b8C2
Child result: FINALIZED / MAJORITY_AGREE, GenVM execution ERROR, value_credited=true
Sender callback get_total_credits: 0
Receiver callback get_total_credits: 0
```

This live result does not prove callback recovery: both counters stayed zero after finalization. The error is retained as a failed test, not a passing recovery. The scripted full lifecycle evidence above applies to the earlier lifecycle deployment, not this recovery deployment. The recovery deployment has one escrow funded through the local frontend smoke test; no lifecycle actions have been run against this smoke-test grant. Vercel was not deployed.

The probe was repeated using a plain native transfer (`emit_transfer`) to a receiver whose `__receive__` raises `gl.vm.UserError` and whose `__on_errored_message__` records a recovery credit:

```text
Probe receiver: 0x0a4CEa3d5F63478424b17B9DB546B3A16f61a4cE
Probe sender: 0x0AFe787a477b65E1045712Bd64E151313FD45bE3
Parent tx: 0xc6885975708c1e8b6738f4a815edca6887bf7e9c2f7601eb2aefa09ce28e465a
Child tx: 0xf491c997fb85653ac5fc1f4e18bb4a375c6693e243abbaf0a9266a5af7b23574
Transfer value: 0.0001 GEN
Parent: FINALIZED / MAJORITY_AGREE / GenVM SUCCESS
Child: FINALIZED / MAJORITY_AGREE / GenVM execution ERROR / value_credited=true
Sender get_total_credits(): 0
Receiver get_total_credits(): 0
```

This second live probe also failed to demonstrate callback delivery or recovery. We explicitly accept this as a documented residual limitation for the current release: outgoing-transfer recovery is not proven safe on StudioNet and must not be described as generally recoverable. Clarity restricts sponsors and payout recipients to direct EOA transactions, but the probes do not prove recovery even for a permitted EOA recipient if GenVM fails before delivering the callback. The receiver's protocol callback is not exposed as an ordinary read method; its dedicated credit getter is the observed zero. Probe sender funding and test transactions were made with the already-unlocked test account, with no grant created.

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

- Run and record the complete lifecycle on the recovery deployment once an EIP-1193 wallet is available to submit the payable grant creation.
- The failed-child callback gap is explicitly accepted as a residual limitation; do not claim general outgoing-transfer recovery is safe. See `docs/SECURITY.md`.
- The owner deploys the frontend to Vercel using `NEXT_PUBLIC_CLARITY_CONTRACT=0xAdC4dEC690a37315FDCC7f50DDE9DDCE3a97379F`.
- Verify injected-wallet behavior and public production reads after the Vercel URL exists.
- Push the source and final live evidence to the owner-supplied GitHub repository and capture the CI run after the current-deployment lifecycle is complete.

No receipt, digest, balance or validator result in this file is simulated. Failed transactions are retained as failures, not counted as successful scenarios.
