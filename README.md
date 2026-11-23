# New Unnamed World — GitHub campaign authority

**Single operational fast-play contract:** [runtime/LIVE_DM_FAST_PATH.md](runtime/LIVE_DM_FAST_PATH.md). Read this after the mandatory repository startup chain. This supersedes contradictory older *procedural* advice; no accepted gameplay, RPG ruling, NPC relationship, DM secret, or owned record is overwritten by a fast-play routing guide.

## Authority and game
Owner-directed cutover 2026-11-20: GitHub owns live text/structured records, Drive Docs/workbooks are historical, art/maps remain Drive/Library. Public DM-only prep is private **in-game**, not access-controlled. Authority: latest explicit player corrections/accepted play → owning GitHub sources → adopted homebrew → 2014 D&D where silent. Check RULES before other 2014 references. Open `migration/TEST_REPORT.md` items remain unverified, never infer a pass.

V controls speech, actions, choices, money and limited features except explicit existing delegation. DM controls NPC/companion motives/actions and genuinely executed dice. Maintain tactical mechanics, appropriate Help, consequential agency and distinct NPC knowledge. Never pre-roll unplayed events, invent resource spend, reset time, reveal DM secrets or turn OOC planning into play.

## Mandatory startup
1. Read `README.md` → `AGENTS.md` → `campaign/continuity/readme.md` → `campaign/continuity/campaign-state.md` for the actual pending V action.
2. Read `automation/recovery/mode.json` and recover the **newer immutable chunk suffix** (when `mode=chunked`; currently active) from `automation/recovery/chunks/D###/` following `automation/recovery/CHUNKS.md`. Do not mistake the empty/old worker compatibility `active.json` for absence of newer accepted play. Compare `runtime/PLAY_NOW.md` against owners and recoveries; newest real accepted state wins.
3. Read `runtime/LIVE_DM_FAST_PATH.md` **once per new conversation**. Consult `runtime/SCENE_CACHE.md` only if its source pins match the scene; consult `runtime/SCENE_CACHE_SPEC.md` when building/repairing that packet, and `runtime/SCOPED_RULES_INDEX.md` only when selecting a needed rules section. Read additional regional/quest/NPC/2014 references only when the scene warrants them. No compulsory blanket prefetch.
4. Resume the exact pending V decision and retain a verified in-conversation tactical/relationship packet. Avoid unrelated audits and replay of previous events.

## During live play
Resolve player action from retained verified facts and necessary scoped source reads, genuine RNG, independent NPC reasoning and 2014 mechanics. Update only changed packet fields. **Every response with accepted gameplay change must create and read back one immutable original chunk** using GitHub `create_file`, stable ID and exact evidence. Do not replace with "unsynced in-conversation only" or wait until the next owner sync. Report failed durability honestly.

At an actual completed combat/exploration/rest/major transaction/quest milestone, ~8–12 substantive changed exchanges or explicit pause/Sync, write one immutable ordered `automation/recovery/boundaries/<ID>.json` manifest. `.github/workflows/immutable-recovery.yml` assembles exact chunks and submits the existing `[CAMPAIGN-SYNC]` PR; independent Work applies owner records, CAMPAIGN_STATE last, verifies and cleans only compatibility entries. Do not poll/wait during active tactical turns. The original chunks remain immutable. Failure to queue is not loss of already saved chunks.

**No model or lore shortcut is authorized.** The fast path removes redundant reads/foreground administration, not relevant facts, fair tactics, NPC agency, plot continuity or meaningful consequences. Approved imagery only at meaningful transitions; no generated campaign art without player request.

## Owners and specialist work
`campaign/continuity/` owns checkpoint, log, RULES, quests, NPCs and custody. `trackers/csv/{v,cirren,fenar}/` and `data/characters/events.csv` own character values. `data/estate/`, `trackers/csv/property/`, `trackers/csv/magic-shops/` own estates and markets; `world/politics/` world canon; `prep/dm-only/` private setup. `runtime/PLAY_NOW.md`, `runtime/REGION_PREP.md`, `runtime/SCENE_CACHE.md`, `dashboard/dashboard.json` are convenience views only. Scheduled specialist tasks and background repairs never advance game time, choose V actions, or automatically merge proposal PRs.

Original full root routing preserved at `archive/continuity/root-readme-before-live-fastpath-20261123.md`.
