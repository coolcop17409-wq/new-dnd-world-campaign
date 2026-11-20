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

## Shared run coordination — RUN-PROTOCOL-v2

The shared protocol retained at [archived protocol](../../archive/continuity/continuity-readme-pre-fastplay.md#shared-run-protocol--run-protocol-v2-2026-11-18) continues to govern causal prerequisites, durable draws, recovery and per-consumer acknowledgements. Its archived writer slot is historical. After cutover, this live README owns the single active slot below; GitHub blob/head expected-SHA guards replace Google document revision guards. Owner journals hold prepared/resolved events and recovery receipts. No change to campaign time or player authority.

CAMPAIGN_WRITER | state=ACTIVE | token=ESTATE-D244-20261120-01 | worker=Estate Ledger Updates | operations=E244-01 | acquired=2026-11-20T10:21:00Z | heartbeat=2026-11-20T10:36:20Z | expires=2026-11-20T10:46:20Z | recovery=data/estate/operational-checkpoint.csv
