# New Unnamed World Campaign — live GitHub authority

Since owner-directed cutover on 2026-11-20, GitHub owns the live campaign text and structured records. Drive Docs/workbooks are historical; maps and large images remain in their designated Drive/Library sources. This public repo includes DM-only preparation: labels govern in-game revelation, not access. `migration/TEST_REPORT.md` retains unresolved evidence-based checks.

## Fast startup
Read `README.md` → `AGENTS.md` → `campaign/continuity/readme.md`, followed by authoritative `campaign/continuity/campaign-state.md`, generated `runtime/PLAY_NOW.md`, and **only the newest played event** at the start of `campaign/continuity/session-log.md`. Cross-check the actual latest event ID and checkpoint, not just the same day. Read applicable RULES, eligible current-region prep/delivery queue and affected NPC/quest/custody sections *only as needed*. Do not automatically fetch huge archives, full trackers, estate, market or whole-world references.

## Source ownership
`campaign/continuity/`: checkpoint, recent log, rules, quests, NPCs, shared custody. `data/characters/events.csv` and `trackers/csv/{v,cirren,fenar}/`: actual personal events and opening baselines. `data/estate/`, `trackers/csv/property/`, `trackers/csv/magic-shops/`: estate and markets. `world/politics/`: world canon; `prep/dm-only/`: unrevealed preparation. `archive/`: closed exact evidence; `dashboard/dashboard.json` and `runtime/PLAY_NOW.md`: generated nonauthoritative views.

See `migration/ONGOING_UPDATE_PROTOCOL.md` for guarded idempotent writing. Batch owner updates at natural play boundaries, **commit CAMPAIGN_STATE last**, then let fast-play refresh the packet asynchronously. Validation failures use the existing queue via `automation/handoffs/sync-repair/README.md`; live narration does not wait for CI/repair. Journal-only updates at unchanged checkpoint need an explicit manual fast-play refresh. No schedule advances game time or V's choices. Never invent events to satisfy tests.

The full preceding README is preserved verbatim at `archive/continuity/root-readme-day265-pre-performance-repair.md`.
