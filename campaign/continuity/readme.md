# Campaign continuity — active GitHub routing

**Authority:** latest explicit player corrections/accepted play → GitHub owning sources → adopted homebrew → 2014 5e. Earlier Drive Docs and Sheets are historical, maps/art remain Drive/Library. Public DM-only GitHub prep is not in-game public knowledge. Original routing preserved verbatim at `archive/continuity/continuity-readme-before-live-fastpath-20261123.md`.

## Exact new-chat startup
Read `README.md` → `AGENTS.md` → this file → `campaign/continuity/campaign-state.md`. Read `automation/recovery/mode.json` and the later **immutable accepted chunk suffix** (`automation/recovery/chunks/D###/`, see `automation/recovery/CHUNKS.md`) after last verified owner/boundary; `active.json` in chunked mode is *worker compatibility only*. Cross-check `runtime/PLAY_NOW.md` and beginning of `session-log.md`, but owner plus newer accepted recovery win. Verify latest pending V choice, not just game day. Read `runtime/LIVE_DM_FAST_PATH.md` once; consult `runtime/SCENE_CACHE.md` only when its pins match the current scene, `runtime/REGION_PREP.md` for relevant locale changes, and `runtime/SCOPED_RULES_INDEX.md` and actual scoped RULES only when required. `runtime/SCENE_CACHE_SPEC.md` is a reference for cache reconstruction, not an extra mandatory read. Fetch eligible current-region DM prep/NPC/quest/custody narrowly. All runtime scene/region files are **nonauthoritative** and can be stale.

## Every changed play response
Play faithfully with actual dice, independent motives, tactical 2014 rules, agency and appropriately narrow new-source checks. Keep a source-pinned in-conversation scene packet, refreshing only changed/unknown material; preserve lore/deep research when consequential. **Always create and verify one immutable recovery chunk per changed response**—never "in-conversation only" until a future batch. No per-turn complete owner writes, CI waits, repetitive whole-canon audits or extra performance log commits.

## Natural sync / specialist background
Only at combat/exploration/quest/rest/major transaction milestone, ~8–12 substantive changes, or explicit pause/end/Sync: create one ordered immutable boundary manifest. Existing GitHub Actions `immutable-recovery.yml` verifies exact hashes and builds a v1 compatibility journal for `[CAMPAIGN-SYNC]` Work worker. Owning changes are posted with guarded stable IDs and CAMPAIGN_STATE **last**; complete validated receipts authorize compatibility cleanup, while original chunks remain forever. A chunk write establishes durability, **not owner-sync completion**. Never choose V's action, invent dice/time, reroll accepted evidence or automatically merge repair/transport PRs.

## Owning files
- `campaign/continuity/campaign-state.md`: current confirmed owner pause; `session-log.md`: recent played evidence; `archive/`: closed exact history
- `rules*.md`: mechanics; `quests.md`, `npcs.md`, `inventory.md`: quest progress, knowledge and custody
- `trackers/csv/{v,cirren,fenar}/` and `data/characters/events.csv`: character sources
- `trackers/csv/property/` and `data/estate/`: businesses; `trackers/csv/magic-shops/`: markets
- `world/politics/`: established political canon; `prep/dm-only/`: eligible secret prep
- `runtime/PLAY_NOW.md`, `runtime/REGION_PREP.md`, `runtime/SCENE_CACHE.md`, `dashboard/dashboard.json`: convenience, never authorities

Keep this index under 8,000 characters; checkpoint under 12,000; recent SESSION_LOG under 75,000. Archive exact text before trimming. Do not assume historic `migration/TEST_REPORT.md` pending checks are resolved.

## Atlas and maintenance pointers
Previously verified atlas `ATLAS-D281-KESTREL-APPROACH-001` is historical to the current region; current overlays and maintenance receipts belong in their respective owning registers, not this startup. Former specific file links and writer-lease receipts remain preserved in `archive/continuity/continuity-readme-before-live-fastpath-20261123.md`.

## Cooperative writer
Short owning-record batch coordination; accepted-play recovery retains its separate fast path.

CAMPAIGN_WRITER | state=HELD | token=SHOPS-POOL5X-20261123-01 | claimed_UTC=2026-11-23T22:19:30.118Z | expires_UTC=2026-11-23T22:29:30.118Z | scope=trackers/csv/magic-shops | recovery=ADMIN-SHOP-POOL-5X-20261123-001
