# Continuity — active GitHub routing

This short file is the live routing index following the owner-authorized GitHub cutover. Read repository [README](../../README.md) and [AGENTS](../../AGENTS.md) first. Historical Google Docs and workbook exports are **not** write targets. The full, pre-optimization routing document is archived intact at [continuity-readme-pre-fastplay.md](../../archive/continuity/continuity-readme-pre-fastplay.md).

## Fast startup, one load per conversation

1. Read [campaign-state.md](campaign-state.md) for the **exact** latest played checkpoint and pending player choice; it now holds only the current checkpoint. Read [runtime/PLAY_NOW.md](../../runtime/PLAY_NOW.md) for concise character counters and scene context. PLAY_NOW is generated; when its checkpoint/day or resource data disagrees with the owning sources, **the owning sources win**. A missing/stale packet is not permission to guess.
2. Read [rules.md](rules.md) and relevant sections of [rules-combat-recovery.md](rules-combat-recovery.md), [rules-dm-procedures.md](rules-dm-procedures.md), or other rules only as required. Approved homebrew and D&D 5e **2014** apply.
3. Read only the recent relevant events in [session-log.md](session-log.md), and scoped [quests.md](quests.md), [npcs.md](npcs.md), [inventory.md](inventory.md), and eligible matching [DM-prep index](../../prep/dm-only/) or current-region outline. Closed history through243 (legacy filename retained): [archive](../../archive/continuity/session-log-days216-231-legacy.md).
4. For exact personal values consult [dashboard/dashboard.json](../../dashboard/dashboard.json), then owning character CSV baselines plus [character events](../../data/characters/events.csv) if challenged or changed. Trackers are not a rules engine. Estate and Magic Shops records are separate and read only when relevant.

## Combat and scene fast path

Keep an in-conversation tactical packet: initiative/turn, positions, cover, creature defenses/HP, party resources, conditions/durations, reactions, NPC motives, outstanding effects and pending V action. Adjudicate each turn using the retained verified packet and genuine RNG; never re-fetch whole logs, rules, art, shops or estates by default. V controls V's speech/actions/dice except for explicit current delegation; independent companions act under DM control.

Maintain a compact **unsynchronized** event ledger during play. Batch guarded, idempotent owner-file writes at combat end, significant exploration, qualifying rest, major transactions, quest/NPC milestones, 8–12 substantive exchanges with changes, or requested pause/sync. Do not interrupt a live tactical turn solely for routine administrative writes. Commit CAMPAIGN_STATE last after verifying the owning changes. For GitHub update and retry rules see [ongoing update protocol](../../migration/ONGOING_UPDATE_PROTOCOL.md).

## Authoritative owners

- [campaign-state.md](campaign-state.md) — exact present and pending player choice.
- [session-log.md](session-log.md) — recent accepted gameplay; archives retain older history.
- [rules.md](rules.md), [rules-combat-recovery.md](rules-combat-recovery.md), [rules-dm-procedures.md](rules-dm-procedures.md), [rules-estate-economy.md](rules-estate-economy.md), [rules-travel-communication.md](rules-travel-communication.md) — mechanics.
- [quests.md](quests.md), [npcs.md](npcs.md), [inventory.md](inventory.md) — established objectives, identities and shared custody.
- [world/politics](../../world/politics/) — world canon. [prep/dm-only](../../prep/dm-only/) — unrevealed preparation, never automatically player-known (the public repository does not restrict access).
- [data/characters](../../data/characters/), [data/estate](../../data/estate/), [trackers/csv/magic-shops](../../trackers/csv/magic-shops/) — owning change journals and market records. CSV character/property baselines retain original values before later events.
- [runtime/PLAY_NOW.md](../../runtime/PLAY_NOW.md) — **generated nonauthoritative fast read**, never a parallel campaign journal. [archive/continuity](../../archive/continuity/) preserves historical material.
- Maps and large images stay in Drive/Library under the established asset/atlas procedures.

## Integrity

No new in-world events, rolls, NPC choices, property operations, income, rests or resources arise from document restructuring, workflow execution or real-world time. Do not treat forecast, proposals, DM secrets or unclosed post-cutover validation items as settled fact. Failed writes remain unsynced until correctly retried without duplicate IDs.

## Current quest preparation and owner handoffs

Quest/prep review ADMIN-QUEST-D244-20261120-01 is scoped to D243-244-WOLVES-REST-AND-BLACKTHORN-RETURN-001, Day244 early evening at Blackthorn. [QUESTS](quests.md) and the [existing private index](../../prep/dm-only/dm-only-secret-quest-outlines.md) carry reconciled status; load that index's current-region owner for delivery. CAMPAIGN_STATE remains the exact pause. Ready preparation is not a delivered invitation, report, scene or player choice.

Record Maintenance Q244-MAINT-01: ADMIN-MAINT-D244-20261120-01 repairs supported NPCS/INVENTORY captions and the missing personal compact custody leg. Closed log blocks through243 were moved after exact destination verification. Accepted Day231–233 summaries are sourced there; original scene transcripts and exact compact clauses remain unresolved, not reconstructed. The private maintenance receipt owns detailed per-consumer status. This is a bounded correction, not completion of migration/TEST_REPORT.md.

Specialist coverage Q244-03: quest implications of D244-ESTATE-CATCHUP-001, including the late visiting-horse request, are incorporated in existing prep; per-effect verified ACKs belong in its private review receipt. Estate accounts/requests, market stock and atlas canon remain owned separately. Actual report delivery and other consumers' ACKs remain pending. Check relevant late market/estate receipts directly before contact or travel, even at an unchanged day.

## ATLAS-PENDING — public evidence queue

Atlas owner only: master v4 receipt ATLAS-D231-20261119-01 was inspected; its scope does not ACK the effects below. Retained pointers are carried forward from the archived README, not new duplicate gameplay postings. Match source + consumer + effect key before applying; close only that effect after verified atlas ACK. The master/derivatives are unchanged by this quest review. No approximate map point creates mileage, ownership, safe passage or a service.

| Source / effective time | Effect key / public scope | Owner evidence and next check |
|---|---|---|
| D231-ESTATE-CATCHUP-001 /225–228 | REEDBED-SERVICE-225-228 | Existing operational service facts; archived README pointer and estate records. Preserve limited local scope, no new regional release. |
| D231-MIREGATE-TRANSFER-FARM-RETCON-001 /231 | MIREGATE-INTERNAL-PLOT | Existing internal four-acre plot adoption; estate/canon evidence. No expanded deed or planted crop inferred. |
| D231-REEDBED-PASSING-TRADE-RETRO-001 /225–231 morning | REEDBED-WALKIN-SERVICES | Existing settled local passing-trade service pointer; no invented scheduled route. |
| D231-ESTATE-BOATS-RETRO-001 /229–230 (recorded231) | REEDBED-OWNED-LOCAL-FLEET | Local12t/10t capacities remain distinct from upper-reach qualification, still unresolved in D244 estate receipt. |
| Archived accepted Day232 closure /232 | RETHWYN-BURIAL-CAPTION-232 | archive/continuity/campaign-state-full-snapshot-pre-fastplay.md explicit completed village burial/marker paragraph; quest closure now reconciled. Standalone original event ID not recovered; no invented coordinates or new site. Apply only an existing relevant caption/register. |
| D234-235-RIVER-HERON-DELEGATION-RETCON-001 and D235-236-RIVER-HERON-VOYAGE-ARRIVAL-001 /234–236 | HERON-UPPER-LANDING-MIREGATE-PILOT | session-log.md: accepted professional clearances and actual downstream passage235 evening→236 late evening. Upper commercial landing is reached from Rethwyn by the accepted road, not river frontage at the manor. Actual eight-ton Heron pilot does not qualify other hulls or create a scheduled passenger service. |
| D236-237-MIREGATE-REST-UPRIVER-001 and D237-238-SNAKE-AFTERMATH-REST-RETURN-001 /237–238 | MIREGATE-UPPER-LANDING-RETURN | session-log.md: two operated small craft, upriver237–238, then coach recovered and Rethwyn return238 evening. Preserve crew/capacity restrictions and direction; no guaranteed universal duration. |
| D241-243-BLACKTHORN-ROAD-001 and D243-244-WOLVES-REST-AND-BLACKTHORN-RETURN-001 /241–244 | RETHWYN-BLACKTHORN-PLAYED-ROAD | session-log.md: four ordinary wagon days actually traveled241–244; trade-road then upland approach. No exact surveyed distance, shortcut or Blackthorn river frontage. |
| D243-244-WOLVES-REST-AND-BLACKTHORN-RETURN-001 /244 | UPLAND-ROADSIDE-OBSERVATION | session-log.md: stone shelter remains and vegetated paved spur observed while remaining on the road. Regional/unlocated observation only; no entered site, known endpoint, title, hazard or new map coordinate. |

## Record Maintenance — ADMIN-MAINT-D244-20261120-01

Status COMMITTED / VERIFIED. Scope: current party/custody captions; accepted Day231–233 evidence recovery; closed log archival through243; scoped written route qualifications and current-region factual readiness. Latest played checkpoint remains D243-244-WOLVES-REST-AND-BLACKTHORN-RETURN-001, Day244 early evening, Blackthorn gate/yard. Previous specialist baseline231 late morning is thirteen campaign day numbers earlier; no exact elapsed hours inferred. Latest offscreen producer receipts are separately D244-ESTATE-CATCHUP-001 and ADMIN-MARKET-D244-20261120-01, not new played scenes or delivered reports.

Operations: M244-A archive destination verification before any source removal; M244-B NPC/custody/history/geography/prep repairs; M244-C missing personal inventory leg and generated-view rebuild; M244-D per-file verification/recheck/release. Expected values: omitted Cirren compact entry→one existing signed original; all party counters, personal purse, other gear, estates and market lots unchanged. State blob1430df7ef96e7880118885608abccc9942c04986 is unchanged, so no CAMPAIGN_STATE commit is needed. Prior history and correction trails remain accessible.

- PLAYABLE CONTINUITY: scoped repairs and generated compact item verified; exact arrival/pending player action preserved. No gameplay simulated.
- SPECIALIST COVERAGE: Estates covers closed231–243 and elapsed daytime244, evening/night244 remains open. Markets review recomputed for244 has zero due; future work is not failure. Quest checkpoint matches; late producer consequences remain available directly to live play and next quest review. Atlas v4 scoped metadata was read; existing ATLAS-PENDING effects lack matching ACKs and remain for its next pass. No atlas files changed.
- HISTORICAL PROVENANCE: accepted231–233 summaries recovered without original transcripts/compact clauses; punt restoration invoice and older208–212 supply/rope provenance remain open. Their missing evidence does not block ordinary Blackthorn play or undo accepted outcomes. migration/TEST_REPORT.md remains unchanged.

| Pending effect / owner | Exact interval/event and dependency | Next check |
|---|---|---|
| Original chronology / Record Maintenance | Day231 local answer,232 burial,233 compact; original scene text and exact clauses unavailable | Recover only if original source evidence becomes accessible; preserve accepted summary |
| Punt cost / Estates | MG-PUNT-COST-RECOVERY,231–235 restoration invoice; operational235 status already accepted | Next estate provenance review; no invented payment or renewed repair |
| Visiting feed / Estates | BT-V-HORSES-244; actual244 feed already consumed; estate stores for245 unverified | Before actual245 feeding/restock; no second244 charge |
| Late producer effects / Quest Development and live DM | ADMIN-MARKET-D244-20261120-01 individual source/effect keys; local knowledge only | Relevant contact/time skip and next quest review; each consumer ACK separately |
| Atlas publication / Atlas | Existing public ATLAS-PENDING source/effect rows; v4 receipt covers only its own225–231 scope | Next atlas pass; close matching verified effects only |

Verification: archive commit 683a1ef01cf2f8f30c09c00517be58bb3575c1e5 preceded owning repair commit 96584b321f872a81dea1ea4aa5d8a6bbdd0992e2. All changed owning files and archives were read back exactly; five local regression checks and tracker validation passed, then GitHub fast-play44759767960 and estate-audit44759767896 succeeded. Eleven closed primary event headers remain once; active244 stays recent. CAMPAIGN_STATE and migration/TEST_REPORT.md are unchanged. The workflow's default undated market queue was regenerated without a campaign day; use the independently verified explicit244 zero-due result in this receipt rather than treating an unbound queue as coverage. Detailed fingerprints and per-file evidence are in the existing private maintenance receipt. No whole-campaign completion claimed.

## Shared run coordination — RUN-PROTOCOL-v2

The shared protocol retained at [archived protocol](../../archive/continuity/continuity-readme-pre-fastplay.md#shared-run-protocol--run-protocol-v2-2026-11-18) continues to govern causal prerequisites, durable draws, recovery and per-consumer acknowledgements. Its archived writer slot is historical. After cutover, this live README owns the single active slot below; GitHub blob/head expected-SHA guards replace Google document revision guards. Owner journals hold prepared/resolved events and recovery receipts. No change to campaign time or player authority.

CAMPAIGN_WRITER | state=ACTIVE | token=PUNT-RECON-D244-20261120-01 | worker=punt-reconciliation | operations=PR244-A,PR244-B | acquired_UTC=2026-11-20T16:58:58.025Z | heartbeat_UTC=2026-11-20T16:58:58.025Z | expires_UTC=2026-11-20T17:08:58.025Z | recovery=data/estate/operational-checkpoint.csv D244-MIREGATE-PUNT-COST-RECON-001

## Estate retrospective correction — D244-ESTATE-REDO-D200-001

Explicit player instruction authorizes bounded estate replacement200–244. Current owners:data/estate/R200-FIN manifests,signedcorrections,Blackthornreplacementops; oldrows/dice remain superseded evidence. Latest checkpoint D244-V-SECOND-WIND-REST-CORRECT-001 over unchanged D243-244-WOLVES-REST-AND-BLACKTHORN-RETURN-001 pause,Day244earlyevening;close243/elapsed244 only; Vactions/resources unchanged. ADMIN-ESTATE-REDO-D244-001 ownsverification. New producer effect R200-ESTATE-RESULTS-AND-REPORT PENDING separate Quest/live-DM/Maintenance ACK; oldcatchupACKs cannot acknowledge changedoutcomes. Neverreroll savedreplacementdraws.

Additional ATLAS-PENDING effects; no matchingACK yet:

| Source | Effect key | Estate-source scope; atlas unchanged |
|---|---|---|
| D244-ESTATE-REDO-D200-001 /222 | R200-REEDBED-SERVICE-222 | Safe yard service begins222; corrects old225/228dates,16t/daydock unchanged. |
| D244-ESTATE-REDO-D200-001 /225 | R200-FORT-DUTY-225 | Existingcharter daylightduty225; no toll/sovereignty/newmappedgeography. |
| D244-ESTATE-REDO-D200-001 /238–243 | R200-BARGE01-UPPER-8T | Specificownedhull8t testedcorridor and actualcustomervoyage; no unrestrictedregional/secondhullcertification. |

Earlier REEDBED-SERVICE-225-228 is superseded for currentdating by R200-REEDBED-SERVICE-222; retain auditpointer/scopedhistoricalACK. Only atlasowner canACK/application-close replacementeffects.

Verification: ADMIN-ESTATE-REDO-D244-001 is VERIFIED. Source commit `e262ef22a22c47e9e64c5d3754374ad7d9ed9e94`, generated-report recovery `ad16a4a0f90878ee65175c49575108ac51036c53`, full estate audit [44772309644](https://github.com/coolcop17409-wq/new-dnd-world-campaign/actions/runs/44772309644) SUCCESS. Day244 early-evening checkpoint rechecked unchanged after the latest Second Wind correction. This completes the authorized estate-result redo; Miregate's historical punt invoice remains a financial-input gap, and consumer ACKs/report delivery remain separate.

## Estate customer acquisition — D244-ESTATE-PROSPECT-SINCE-START-001

COMMITTED / VERIFIED: standing active prospecting covers every actual or realistically producible estate offering from each steward’s evidenced beginning. Current briefs/continuing requests, fourteen newly adjudicated independent responses, eight assents, actual fulfillment, custody and exact net corrections are in the existing estate journals. Prior historical all-output sales, named customer decisions, passing demand, Day200 redo and funding legs remain once. Ordinary new Orsaven business no longer waits for V to choose the customer. No automation schedule/settings changed.

Owner commit 0e1ed20c9f34c7bc29c05b7bd73fd41bcf0f37fa was read back exactly across fifteen changed files; estate audit 44776631711 succeeded with nineteen tests, replay, cumulative tax, tracker checks and generated views. Daily cash, actual stock/reservations and storage capacity reconcile. Current checked checkpoint remains D244-V-SECOND-WIND-REST-CORRECT-001, Day244 early evening: full close243 plus elapsed244 only. No new completed day or V action/resource change.

Additional cash from completed new business: Blackthorn132gp, Miregate23.06gp, Reedbed28gp; Fort unchanged. Current accounts: Blackthorn822.80cash/215.36actual obligations/607.44available; Miregate395.66/11.38/384.28; Reedbed171/8.60/162.40; Fort5.71/7.85/−2.14, with171.43earned receivable including120due245. No reserve deduction. Current storage includes MiregatePS-MG-F4t customergrain through246,1.15unearned advance. BlackthornPS-BT-E1t architectural253order is28gp unearned; actual.114t reserved, .886t future production. Current reports own subsequent balances.

Scope limits remain explicit: Miregate historic231–235punt rebuild invoice is unavailable (operational235 status unaffected); Caereth carrier/sample replies and four-acre crop season/full-cost offtake remain their existing actionable requests. This receipt verifies the new customer-development reconciliation, not every historical campaign discrepancy or those unperformed proposals. Existing migration validation items and ATLAS-PENDING effects remain open.

| Producer source/effect | Consumer | Actual knowledge / earliest contact | ACK |
|---|---|---|---|
| ESTATE-PROSPECT-START-D244-20261120-01 / PS244-CUSTOMER-DEVELOPMENT; source D244-ESTATE-PROSPECT-SINCE-START-001 | Live DM | Tamsin knows local orders now and can report at actual244yard conversation; river results require an actual Meret message/visit. No player speech or Sending Stone use assumed. | PENDING |
| Same source/effect | Quest Development | Use saved current estate readiness and requests at next relevant preparation; no forced hook or invented news delivery. | PENDING |
| Same source/effect | Record Maintenance | Verified owners and custody are available; retain own per-consumer application evidence. Earlier redo ACK is not this effect’s ACK. | PENDING |

No new public geographic service/access change is introduced by marketing existing services; no new atlas effect or fabricated ACK. ADMIN-ESTATE-PROSPECT-D244-001 and PS244-HANDOFF-* own exact verification and pending consumers. Successful accounting cutoffs were retained and annotated only after dependent owner writes verified.
