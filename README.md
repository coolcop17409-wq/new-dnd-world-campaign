# New Unnamed World Campaign — live GitHub authority

## Per-response recovery — owner-authorized 2026-11-21

For changed gameplay, save exactly one small validated recovery entry to `automation/recovery/active.json` with a **file-blob-SHA guarded single-file update** and readback per `automation/recovery/README.md`. This is the owner-authorized per-response exception to no-per-turn writes. Never sync full owning records, poll CI, conduct external research or wait for a repair worker during an active combat turn. At startup reconcile recovery with current owners; only verified events may be cleared. Recorded is not queued or fully synced; a failed recovery write remains unsaved. No capture after a chat closes is guaranteed.

Since owner-directed cutover on 2026-11-20, GitHub owns the live campaign text and structured records. Drive Docs/workbooks are historical; maps and large images remain in their designated Drive/Library sources. This public repo includes DM-only preparation: labels govern in-game revelation, not access. `migration/TEST_REPORT.md` retains unresolved evidence-based checks.

## Active combat: pinned facts, zero repeat research

Current combat reuses the verified in-conversation tactical packet. For the ongoing Day266 troll encounter, the compact **static** source reference is `runtime/COMBAT_SOURCE_PIN.md` and changing tactical facts belong to the latest accepted in-conversation actions and `automation/recovery/active.json`. Read each source at most once per relevant scene/startup, not every combat turn. The source pin never overrides newer accepted play. Execute fresh genuine DM dice as needed; no web search or monster/stat lookup for an already pinned creature. Per-response recovery is the only routine GitHub write and should not delay the playable answer with CI or owner sync.

## Fast startup
Read `README.md` → `AGENTS.md` → `campaign/continuity/readme.md`, followed by authoritative `campaign/continuity/campaign-state.md`, generated `runtime/PLAY_NOW.md`, and **only the newest played event** at the start of `campaign/continuity/session-log.md`. Cross-check the actual latest event ID and checkpoint, not just the same day. Read applicable RULES, eligible current-region prep/delivery queue and affected NPC/quest/custody sections *only as needed*. Do not automatically fetch huge archives, full trackers, estate, market or whole-world references.

## Source ownership
`campaign/continuity/`: checkpoint, recent log, rules, quests, NPCs, shared custody. `data/characters/events.csv` and `trackers/csv/{v,cirren,fenar}/`: actual personal events and opening baselines. `data/estate/`, `trackers/csv/property/`, `trackers/csv/magic-shops/`: estate and markets. `world/politics/`: world canon; `prep/dm-only/`: unrevealed preparation. `archive/`: closed exact evidence; `dashboard/dashboard.json` and `runtime/PLAY_NOW.md`: generated nonauthoritative views.

See `migration/ONGOING_UPDATE_PROTOCOL.md` for guarded idempotent writing. Batch owner updates at natural play boundaries, **commit CAMPAIGN_STATE last**, then let fast-play refresh the packet asynchronously. Validation failures use the existing queue via `automation/handoffs/sync-repair/README.md`; live narration does not wait for CI/repair. Journal-only updates at unchanged checkpoint need an explicit manual fast-play refresh. No schedule advances game time or V's choices. Never invent events to satisfy tests.

The full preceding README is preserved verbatim at `archive/continuity/root-readme-day265-pre-performance-repair.md`.

## Automatic background synchronization — owner-authorized 2026-11-21

At normal sync boundaries, automatically submit accepted changes using `automation/handoffs/play-sync/README.md`; do not ask the player to trigger or approve each handoff. This supersedes foreground multi-file synchronization at those boundaries. The playing chat performs the durable request/PR submission, then continues; the background worker validates and applies owning records, checkpoint last. Say queued only after readback, saved only after the verified applied receipt, and unsaved if submission failed. At startup recover relevant pending `[CAMPAIGN-SYNC]` batches and dependencies before resuming; never replay their accepted events. No invisible capture after chat closure, per-turn admin, invented evidence or automatic PR merge. Explicit requests to wait for completed saving must report actual completion or pending status.
