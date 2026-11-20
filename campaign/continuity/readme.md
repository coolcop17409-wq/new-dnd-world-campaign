# Continuity — active GitHub routing

This short file is the live routing index following the owner-authorized GitHub cutover. Read repository [README](../../README.md) and [AGENTS](../../AGENTS.md) first. Historical Google Docs and workbook exports are **not** write targets. The full, pre-optimization routing document is archived intact at [continuity-readme-pre-fastplay.md](../../archive/continuity/continuity-readme-pre-fastplay.md).

## Fast startup, one load per conversation

1. Read [campaign-state.md](campaign-state.md) for the **exact** latest played checkpoint and pending player choice; it now holds only the current checkpoint. Read [runtime/PLAY_NOW.md](../../runtime/PLAY_NOW.md) for concise character counters and scene context. PLAY_NOW is generated; when its checkpoint/day or resource data disagrees with the owning sources, **the owning sources win**. A missing/stale packet is not permission to guess.
2. Read [rules.md](rules.md) and relevant sections of [rules-combat-recovery.md](rules-combat-recovery.md), [rules-dm-procedures.md](rules-dm-procedures.md), or other rules only as required. Approved homebrew and D&D 5e **2014** apply.
3. Read only the recent relevant events in [session-log.md](session-log.md), and scoped [quests.md](quests.md), [npcs.md](npcs.md), [inventory.md](inventory.md), and eligible matching [DM-prep index](../../prep/dm-only/) or current-region outline. Full older log: [archive](../../archive/continuity/session-log-days216-231-legacy.md).
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

Record Maintenance handoff Q244-MAINT-01: verify remaining NPCS/INVENTORY summary and custody captions against the accepted archived checkpoint, and recover missing standalone Day231–233 chronology where original evidence is available. Exact locators and limitations are in the existing private review receipt; preserve accepted closure and never fabricate missing dialogue/rolls. Character journal overlay coverage remains with its owner. This is a bounded provenance/caption follow-up, not failed gameplay and not completion of migration/TEST_REPORT.md.

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

## Shared run coordination — RUN-PROTOCOL-v2

The shared protocol retained at [archived protocol](../../archive/continuity/continuity-readme-pre-fastplay.md#shared-run-protocol--run-protocol-v2-2026-11-18) continues to govern causal prerequisites, durable draws, recovery and per-consumer acknowledgements. Its archived writer slot is historical. After cutover, this live README owns the single active slot below; GitHub blob/head expected-SHA guards replace Google document revision guards. Owner journals hold prepared/resolved events and recovery receipts. No change to campaign time or player authority.

CAMPAIGN_WRITER | state=IDLE | last_token=QUEST-D244-20261120-01 | last_operation=Q244-01,Q244-02,Q244-03 | recovery=prep/dm-only/dm-only-secret-quest-outlines.md ADMIN-QUEST-D244-20261120-01 | verified_owner_commit=ae44194ccc28bd21bd0e0dbc3c80508df9d8816e | verified_coverage_commit=b8f959872a87ece45c9566b5b2147c24b5a77ee4
