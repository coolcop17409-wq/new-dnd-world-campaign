# New Unnamed World Campaign — live GitHub authority

## Per-response recovery — owner-authorized 2026-11-21

For changed gameplay, save exactly one small validated recovery entry to `automation/recovery/active.json` with a **file-blob-SHA guarded single-file update** and readback per `automation/recovery/README.md`. This is the owner-authorized per-response exception to no-per-turn writes. Never sync full owning records, poll CI, conduct external research or wait for a repair worker during an active combat turn. At startup reconcile recovery with current owners; only verified events may be cleared. Recorded is not queued or fully synced; a failed recovery write remains unsaved. No capture after a chat closes is guaranteed.

Since owner-directed cutover on 2026-11-20, GitHub owns the live campaign text and structured records. Drive Docs/workbooks are historical; maps and large images remain in their designated Drive/Library sources. This public repo includes DM-only preparation: labels govern in-game revelation, not access. `migration/TEST_REPORT.md` retains unresolved evidence-based checks.

## Active combat: pinned facts, zero repeat research

Active combat reuses the verified in-conversation encounter packet and genuine DM dice. A pinned monster/source reference is valid only for its named **currently active** encounter; the old `runtime/COMBAT_SOURCE_PIN.md` records the completed Day266 trolls and must not be loaded as a live Day278 encounter. Do not repeatedly fetch known stats or poll CI. Changed play receives one small recovery entry; owner synchronization stays in background.

## Fast startup
Read `README.md` → `AGENTS.md` → `campaign/continuity/readme.md`, followed by authoritative `campaign/continuity/campaign-state.md`, generated `runtime/PLAY_NOW.md`, and **only the newest played event** at the start of `campaign/continuity/session-log.md`. Cross-check the actual latest event ID and checkpoint, not just the same day. Read applicable RULES, eligible current-region prep/delivery queue and affected NPC/quest/custody sections *only as needed*. Do not automatically fetch huge archives, full trackers, estate, market or whole-world references.

## Source ownership
`campaign/continuity/`: checkpoint, recent log, rules, quests, NPCs, shared custody. `data/characters/events.csv` and `trackers/csv/{v,cirren,fenar}/`: actual personal events and opening baselines. `data/estate/`, `trackers/csv/property/`, `trackers/csv/magic-shops/`: estate and markets. `world/politics/`: world canon; `prep/dm-only/`: unrevealed preparation. `archive/`: closed exact evidence; `dashboard/dashboard.json` and `runtime/PLAY_NOW.md`: generated nonauthoritative views.

See `migration/ONGOING_UPDATE_PROTOCOL.md` for guarded idempotent writing. Batch owner updates at natural play boundaries, **commit CAMPAIGN_STATE last**, then let fast-play refresh the packet asynchronously. Validation failures use the existing queue via `automation/handoffs/sync-repair/README.md`; live narration does not wait for CI/repair. Journal-only updates at unchanged checkpoint need an explicit manual fast-play refresh. No schedule advances game time or V's choices. Never invent events to satisfy tests.

The full preceding README is preserved verbatim at `archive/continuity/root-readme-day265-pre-performance-repair.md`.

## Automatic background synchronization — owner-authorized 2026-11-21

At a real natural synchronization boundary, the live DM records an explicit `sync_trigger` in the guarded recovery update and separately posts a tiny SHA/digest-pinned `automation/recovery/sync-ready.json` marker at that boundary; ordinary recovery writes never trigger Actions. **GitHub Actions** then independently pins the journal, discovers old requests, constructs an immutable batch and opens a deduplicated draft `[CAMPAIGN-SYNC]` PR; ChatGPT Work applies verified owner changes and checkpoint last. This replaces foreground PR construction, not the per-response durable recovery requirement. Never infer boundaries from ordinary actions, promise immediate delivery, or claim queued until a PR exists; say **recovery recorded, handoff requested** after readback. Existing manually queued transports remain valid. If Actions fails, keep the journal and let maintenance retry without duplicating IDs. No unsupervised gameplay, PR merges or after-close event capture. See `automation/recovery/README.md`.
