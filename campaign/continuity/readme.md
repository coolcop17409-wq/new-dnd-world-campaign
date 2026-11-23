# Continuity — live GitHub routing

The owner's 2026-11-20 GitHub cutover remains active. This file is a **short index**, not a gameplay journal. Historical Drive Docs/workbooks are read-only references; maps/large images remain in Drive/Library. Public DM-only material still has in-game revelation restrictions. Superseded routing text is preserved verbatim in `archive/continuity/continuity-routing-before-auto-sync-20261121.md`.

## Mandatory scoped startup
1. Read repository `README.md` → `AGENTS.md` → this routing index.
2. Read `campaign/continuity/campaign-state.md` (exact owner checkpoint), `runtime/PLAY_NOW.md` (generated counters/summary) and `automation/recovery/active.json` (accepted unsynced play). Compare current checkpoint, newest SESSION_LOG ID and pinned request receipts; owner and newer accepted play override generated views.
3. Read only applicable `campaign/continuity/rules*.md`, recent relevant `session-log.md`, active `quests.md`, `npcs.md`, `inventory.md`, and eligible current-region `prep/dm-only/` sections. `runtime/REGION_PREP.md` is a *DM-only convenience briefing*; check its checkpoint against the actual scene. If stale, use owning references.
4. Use `dashboard/dashboard.json` only for missing/disputed counters; owning character CSVs and `data/characters/events.csv` control actual changes. Do not bulk-read archives, full NPCS/QUESTS, estates, shops, world politics or visuals unless relevant.

## Fast live play and record durability
Retain one verified in-conversation scene/tactical packet; genuine DM dice, independent companions and V-controlled actions remain mandatory. Do not reread known monster/character sources or conduct background accounting during a turn.

Each response with new accepted play appends exactly one guarded recovery entry in `automation/recovery/active.json`. At an actual natural sync boundary, include the explicit validated `sync_trigger` marker in that same update (or use a guarded marker-only update for explicit Sync when unqueued entries already exist). **GitHub Actions**, not the live DM, discovers prior PRs, pins the journal, builds the immutable request and opens the draft `[CAMPAIGN-SYNC]` transport. The independent Work worker applies accepted owning events, CAMPAIGN_STATE last, verifies and prunes covered recovery. The DM need not wait for Actions or investigate repair logs while narrating. A saved recovery entry is not a queued or owner-synced result. Marker without durable readback is unsaved; worker may not advance V or invent events.

Fallback, exact marker schema, prior-request discovery, supersession, retries and verified-only cleanup: `automation/recovery/README.md`, `automation/handoffs/play-sync/README.md` and `migration/ONGOING_UPDATE_PROTOCOL.md`. Technical validation failures route to `automation/handoffs/sync-repair/README.md` and cannot automatically merge unreviewed fixes. Never silently claim completed saving.

## Owning records
- `campaign/continuity/campaign-state.md`: sole current pause and V pending action; `session-log.md`: recent accepted history; `archive/`: closed evidence
- `rules*.md`: mechanics; `quests.md`, `npcs.md`, `inventory.md`: progress, actor knowledge and shared custody
- `trackers/csv/{v,cirren,fenar}/` + `data/characters/events.csv`: personal baselines and posted changes
- `trackers/csv/property/` + `data/estate/`: property/finances; `trackers/csv/magic-shops/`: dealers, stock and turnover
- `world/politics/`: world canon; `prep/dm-only/`: unplayed secrets and source-eligible scene outlines
- `runtime/PLAY_NOW.md`, `runtime/REGION_PREP.md`, `dashboard/dashboard.json`: nonauthoritative generated/curated convenience only

Keep this index under 8,000 characters, checkpoint under 12,000 and recent SESSION_LOG under 75,000 (preferred 30–45K); archive exact history before trimming. Never convert scheduled preparation, administrative receipts, synthetic tests or real-world time into campaign events. `migration/TEST_REPORT.md` retains unverified cutover items.

## Atlas review

Verified edition `ATLAS-D281-KESTREL-APPROACH-001` · Caer Veylan to Station Kestrel, Day 281 accepted travel. [HTML v11](https://chatgpt.com/library?file_id=libfile_70639e30a8e88191893e8c0afca5ed4b&account_id=personal) · [SVG v8](https://chatgpt.com/library?file_id=libfile_9b506d61a5208191aaa86f32100ecfe0&account_id=personal) · [transparent PNG v3](https://chatgpt.com/library?file_id=libfile_cb3bd386e910819187a767f1b4b6ee7a&account_id=personal) · [preview v7](https://chatgpt.com/library?file_id=libfile_58d6beffe2c481918bffb5c188806a48&account_id=personal). [Previous edition](https://github.com/coolcop17409-wq/new-dnd-world-campaign/blob/89c505ef8291d040189837707f71651efd5ff7a2/campaign/continuity/readme.md#atlas-review).

## Cooperative writer

Shared RUN-PROTOCOL-v2 coordination for short owning-record batches; gameplay recovery uses its separate single-file fast path.

CAMPAIGN_WRITER | state=ACTIVE | token=QUESTS-D281-20261123T1213 | owner=Quest-Development | acquired_UTC=2026-11-23T12:13:19Z | heartbeat_UTC=2026-11-23T12:13:19Z | expires_UTC=2026-11-23T12:23:19Z | scope=quests,index,program,route,ancestry,REGION_PREP | recovery=prep/dm-only/dm-only-secret-quest-outlines.md#current-scoped-verification-and-consumer-handling--admin-quest-d281-20261123-01
