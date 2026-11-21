# Continuity — active GitHub routing

This short file is the live routing index following the owner-authorized GitHub cutover. Read repository [README](../../README.md) and [AGENTS](../../AGENTS.md) first. Historical Google Docs and workbook exports are **not** write targets. The full, pre-optimization routing document is archived intact at [continuity-readme-pre-fastplay.md](../../archive/continuity/continuity-readme-pre-fastplay.md).

## Fast startup, one load per conversation

1. Read [campaign-state.md](campaign-state.md) for the **exact** latest played checkpoint and pending player choice; it now holds only the current checkpoint. Read [runtime/PLAY_NOW.md](../../runtime/PLAY_NOW.md) for concise character counters and scene context. PLAY_NOW is generated; when its checkpoint/day or resource data disagrees with the owning sources, **the owning sources win**. A missing/stale packet is not permission to guess.
2. Read [rules.md](rules.md) and relevant sections of [rules-combat-recovery.md](rules-combat-recovery.md), [rules-dm-procedures.md](rules-dm-procedures.md), or other rules only as required. Approved homebrew and D&D 5e **2014** apply.
3. Read only the recent relevant events in [session-log.md](session-log.md), and scoped [quests.md](quests.md), [npcs.md](npcs.md), [inventory.md](inventory.md), and eligible matching [DM-prep index](../../prep/dm-only/) or current-region outline. Closed history through243 (legacy filename retained): [archive](../../archive/continuity/session-log-days216-231-legacy.md).
4. For exact personal values consult [dashboard/dashboard.json](../../dashboard/dashboard.json), then owning character CSV baselines plus [character events](../../data/characters/events.csv) if challenged or changed. Trackers are not a rules engine. Estate and Magic Shops records are separate and read only when relevant.

## Ordinary turn — no mandatory write

Normal conversation, consenting companion escort, mundane market resupply and movement inside a familiar town use the verified in-conversation packet and change ledger. Narrate first; don't automatically fetch large records, shop catalogs or portraits and **don't trigger a full GitHub sync merely for routine movement or standard provisions**. Sync on actual significant milestones, qualifying rests, major transactions, 8–12 substantive changed exchanges or explicit pause/end; preserve exact unsynced amounts and never claim uncommitted changes were saved. Full procedural rule: `rules-dm-procedures.md` / `migration/ONGOING_UPDATE_PROTOCOL.md`.

## Combat and scene fast path

Keep an in-conversation tactical packet: initiative/turn, positions, cover, creature defenses/HP, party resources, conditions/durations, reactions, NPC motives, outstanding effects and pending V action. Adjudicate each turn using the retained verified packet and genuine RNG; never re-fetch whole logs, rules, art, shops or estates by default. V controls V's speech/actions/dice except for explicit current delegation; independent companions act under DM control.

Maintain a compact **unsynchronized** event ledger during play. Batch guarded, idempotent owner-file writes at combat end, significant exploration, qualifying rest, major transactions, quest/NPC milestones, 8–12 substantive exchanges with changes, or requested pause/sync. Do not interrupt a live tactical turn solely for routine administrative writes. Commit CAMPAIGN_STATE last after verifying the owning changes. For GitHub update and retry rules see [ongoing update protocol](../../migration/ONGOING_UPDATE_PROTOCOL.md).

## Delegated work queue

`automation/handoffs/README.md` routes queued nonplaying preparation to existing daily specialist workers. Live DM can record an immutable request at natural sync and continue play; completion is not instantaneous, and receipts never override owning records or advance V actions. Validation failures use the `sync-repair` lane and isolated draft PRs; detailed procedures live in `automation/handoffs/sync-repair/README.md`. Continue narration from verified facts without polling CI/repair.

## Authoritative owners

- [campaign-state.md](campaign-state.md) — exact present and pending player choice.
- [session-log.md](session-log.md) — recent accepted gameplay; archives retain older history.
- [rules.md](rules.md), [rules-combat-recovery.md](rules-combat-recovery.md), [rules-dm-procedures.md](rules-dm-procedures.md), [rules-estate-economy.md](rules-estate-economy.md), [rules-travel-communication.md](rules-travel-communication.md) — mechanics.
- [quests.md](quests.md), [npcs.md](npcs.md), [inventory.md](inventory.md) — established objectives, identities and shared custody.
- [world/politics](../../world/politics/) — world canon. [prep/dm-only](../../prep/dm-only/) — unrevealed preparation, never automatically player-known (the public repository does not restrict access).
- [data/characters](../../data/characters/), [data/estate](../../data/estate/), [trackers/csv/magic-shops](../../trackers/csv/magic-shops/) — owning change journals and market records. CSV character/property baselines retain original values before later events.
- [runtime/PLAY_NOW.md](../../runtime/PLAY_NOW.md) — **generated nonauthoritative fast read**, never a parallel campaign journal. [archive/continuity](../../archive/continuity/) preserves historical material.
- Maps and large images stay in Drive/Library under the established asset/atlas procedures.

## Atlas review

Verified edition `ATLAS-D266-TARNFORD-COACH-001` · Blackthorn–Nightglass surface road and Tarnford, Day 266. [HTML v9](https://chatgpt.com/library?file_id=libfile_70639e30a8e88191893e8c0afca5ed4b&account_id=personal) · [SVG v6](https://chatgpt.com/library?file_id=libfile_9b506d61a5208191aaa86f32100ecfe0&account_id=personal) · [transparent PNG v3](https://chatgpt.com/library?file_id=libfile_cb3bd386e910819187a767f1b4b6ee7a&account_id=personal) · [preview v5](https://chatgpt.com/library?file_id=libfile_58d6beffe2c481918bffb5c188806a48&account_id=personal). Earlier publications and pending releases: [archived atlas review](../../archive/continuity/readme-day244-246-receipts-before-fastplay-repair.md#atlas-review).

CAMPAIGN_WRITER | state=IDLE | last_token=ESTATES-D266-20261121-1045 | released_UTC=2026-11-21T11:09:11.217Z | result=VERIFIED_DAILY_ACCOUNTING_WITH_SCOPED_HOLDS | recovery=data/estate/operational-checkpoint.csv#ADMIN-ESTATE-D266-20261121-01

## Integrity

No new in-world events, rolls, NPC choices, property operations, income, rests or resources arise from document restructuring, workflow execution or real-world time. Do not treat forecast, proposals, DM secrets or unclosed post-cutover validation items as settled fact. Failed writes remain unsynced until correctly retried without duplicate IDs.

## Maintenance receipts and handoffs

The complete pre-cleanup continuity README, including quest/atlas ACKs, economic corrections, punt reconciliation and all original detailed receipts, is preserved **verbatim** at `archive/continuity/readme-day244-246-receipts-before-fastplay-repair.md`. Consult the current owning QUESTS/NPCS/estate/market/private-prep records for live facts and the archive for provenance. A receipt is not automatic player-facing delivery.

## Compactness

Keep this routing index under 8,000 characters. Do not append dated maintenance reports, acknowledgement trails or played scenes. Put full details in specialist owning journals/reports and add only stable concise pointers here. CAMPAIGN_STATE owns the current pause, SESSION_LOG recent played records and archive older history; PLAY_NOW/dashboard are derived views.
