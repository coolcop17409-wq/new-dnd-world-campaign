# Continuity — live GitHub routing

The owner's 2026-11-20 GitHub cutover remains active. This file is a **short index**, not a gameplay journal. Historical Drive Docs/workbooks are read-only references; maps/large images remain in Drive/Library. Public DM-only material still has in-game revelation restrictions. Superseded routing text is preserved verbatim in `archive/continuity/continuity-routing-before-auto-sync-20261121.md`.

## Mandatory scoped startup
1. Read repository `README.md` → `AGENTS.md` → this routing index.
2. Read `campaign/continuity/campaign-state.md` and `automation/recovery/mode.json`. In active chunked mode recover the newer immutable `automation/recovery/chunks/D###/` suffix under `automation/recovery/CHUNKS.md`; an empty compatibility `active.json` does not mean no newer accepted play. Compare `runtime/PLAY_NOW.md`, newest SESSION_LOG ID and bound receipts against owners plus accepted chunks.
3. Read only applicable `campaign/continuity/rules*.md`, recent relevant `session-log.md`, active `quests.md`, `npcs.md`, `inventory.md`, and eligible current-region `prep/dm-only/` sections. Read `runtime/LIVE_DM_FAST_PATH.md` once at startup. Use `runtime/SCENE_CACHE.md` only with matching source pins and `runtime/REGION_PREP.md` only for relevant locale transitions; stale packets yield to owners/newer accepted chunks. `runtime/SCOPED_RULES_INDEX.md` routes to RULES, never replaces them.
4. Use `dashboard/dashboard.json` only for missing/disputed counters; owning character CSVs and `data/characters/events.csv` control actual changes. Do not bulk-read archives, full NPCS/QUESTS, estates, shops, world politics or visuals unless relevant.

## Fast live play and record durability
Retain one verified in-conversation scene/tactical packet; genuine DM dice, independent companions and V-controlled actions remain mandatory. Do not reread known monster/character sources or conduct background accounting during a turn.

Every changed response creates and reads back exactly **one immutable original chunk**, with stable ID and exact accepted evidence, via GitHub `create_file`. Never append per-turn to `active.json` in chunked mode. At a genuine synchronization threshold create one ordered digest-checked immutable boundary manifest. GitHub Actions assembles the compatibility journal only at that boundary and queues the deduplicated draft `[CAMPAIGN-SYNC]` transport; the independent Work worker applies verified owner events and CAMPAIGN_STATE last. Preserve original chunks permanently. Recovery recorded, PR queued, worker partial and owners verified/cleaned are separate states. Failed readback remains unsaved; retain exact deltas. Do not wait for CI during narration or invent a boundary, V action or outcome.

Mode-specific fallback, prior-request discovery, supersession, retries and verified-only compatibility cleanup: `automation/recovery/CHUNKS.md`, `automation/recovery/README.md`, `automation/handoffs/play-sync/README.md` and `migration/ONGOING_UPDATE_PROTOCOL.md`. Technical validation failures route to `automation/handoffs/sync-repair/README.md` and cannot automatically merge unreviewed fixes. Never silently claim completed saving.

## Owning records
- `campaign/continuity/campaign-state.md`: sole current pause and V pending action; `session-log.md`: recent accepted history; `archive/`: closed evidence
- `rules*.md`: mechanics; `quests.md`, `npcs.md`, `inventory.md`: progress, actor knowledge and shared custody
- `trackers/csv/{v,cirren,fenar}/` + `data/characters/events.csv`: personal baselines and posted changes
- `trackers/csv/property/` + `data/estate/`: property/finances; `trackers/csv/magic-shops/`: dealers, stock and turnover
- `world/politics/`: world canon; `prep/dm-only/`: unplayed secrets and source-eligible scene outlines
- `runtime/PLAY_NOW.md`, `runtime/REGION_PREP.md`, `dashboard/dashboard.json`: nonauthoritative generated/curated convenience only

Keep this index under 8,000 characters, checkpoint under 12,000 and recent SESSION_LOG under 75,000 (preferred 30–45K); archive exact history before trimming. Never convert scheduled preparation, administrative receipts, synthetic tests or real-world time into campaign events. `migration/TEST_REPORT.md` retains unverified cutover items.

## Atlas review

Current edition `ATLAS-D356-REGIONAL-PLACEMENT-001` adds route-relative regional pins for the accepted Silverward and Orseld landmarks. [Verified publication, versions and output hashes](../../assets/README.md#atlas-review).

## Cooperative writer

Shared RUN-PROTOCOL-v2 coordination for short owning-record batches; gameplay recovery uses its separate single-file fast path.

CAMPAIGN_WRITER | state=IDLE | released_UTC=2026-11-28T11:23:44.744Z | previous_token=ESTATE-TOWER-PROFIT-PLAN-20261128-01 | result=VERIFIED | recovery=data/estate/operational-checkpoint.csv#D356-WT-PROFIT-PATH-001; HANDOFF-D344