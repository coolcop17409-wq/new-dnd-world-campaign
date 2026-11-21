# New Unnamed World Campaign — live GitHub authority

## Per-response recovery — owner-authorized 2026-11-21

Before finishing each response that changes accepted campaign state, append and verify a small recovery entry in `automation/recovery/active.json` per `automation/recovery/README.md`. This is the explicit exception to older no-per-turn-GitHub-write instructions; full owner synchronization still occurs at normal boundaries. At startup recover this journal alongside pending play-sync batches before continuing. Clear only exact entries covered by independently verified completed batches, preserving newer entries. Recovery recorded, queued and saved to owners are distinct states. Failed writes remain unsaved; no after-close capture is promised.

Since owner-directed cutover on 2026-11-20, GitHub owns the live campaign text and structured records. Drive Docs/workbooks are historical; maps and large images remain in their designated Drive/Library sources. This public repo includes DM-only preparation: labels govern in-game revelation, not access. `migration/TEST_REPORT.md` retains unresolved evidence-based checks.

## Fast startup
Read `README.md` → `AGENTS.md` → `campaign/continuity/readme.md`, followed by authoritative `campaign/continuity/campaign-state.md`, generated `runtime/PLAY_NOW.md`, and **only the newest played event** at the start of `campaign/continuity/session-log.md`. Cross-check the actual latest event ID and checkpoint, not just the same day. Read applicable RULES, eligible current-region prep/delivery queue and affected NPC/quest/custody sections *only as needed*. Do not automatically fetch huge archives, full trackers, estate, market or whole-world references.

## Source ownership
`campaign/continuity/`: checkpoint, recent log, rules, quests, NPCs, shared custody. `data/characters/events.csv` and `trackers/csv/{v,cirren,fenar}/`: actual personal events and opening baselines. `data/estate/`, `trackers/csv/property/`, `trackers/csv/magic-shops/`: estate and markets. `world/politics/`: world canon; `prep/dm-only/`: unrevealed preparation. `archive/`: closed exact evidence; `dashboard/dashboard.json` and `runtime/PLAY_NOW.md`: generated nonauthoritative views.

See `migration/ONGOING_UPDATE_PROTOCOL.md` for guarded idempotent writing. Batch owner updates at natural play boundaries, **commit CAMPAIGN_STATE last**, then let fast-play refresh the packet asynchronously. Validation failures use the existing queue via `automation/handoffs/sync-repair/README.md`; live narration does not wait for CI/repair. Journal-only updates at unchanged checkpoint need an explicit manual fast-play refresh. No schedule advances game time or V's choices. Never invent events to satisfy tests.

The full preceding README is preserved verbatim at `archive/continuity/root-readme-day265-pre-performance-repair.md`.

## Automatic background synchronization — owner-authorized 2026-11-21

At normal sync boundaries, automatically submit accepted changes using `automation/handoffs/play-sync/README.md`; do not ask the player to trigger or approve each handoff. This supersedes foreground multi-file synchronization at those boundaries. The playing chat performs the durable request/PR submission, then continues; the background worker validates and applies owning records, checkpoint last. Say queued only after readback, saved only after the verified applied receipt, and unsaved if submission failed. At startup recover relevant pending `[CAMPAIGN-SYNC]` batches and dependencies before resuming; never replay their accepted events. No invisible capture after chat closure, per-turn admin, invented evidence or automatic PR merge. Explicit requests to wait for completed saving must report actual completion or pending status.
