# New Unnamed World — asynchronous campaign work handoffs

This is a **work-request queue**, NOT a gameplay journal or separate source of canon. The live campaign runs immediately. Existing scheduled campaign task workers inspect their own lane and do source-verified preparation and maintenance when they next run. Preparation queue creation does **not** trigger an immediate separate chat. The dedicated sync-repair lane opens a draft PR for the configured GitHub-to-Work trigger; actual delivery must be verified, with scheduled fallback.

## Routing

| Lane | Existing scheduled worker | Owner scope |
| --- | --- | --- |
| `shops` | Update campaign magic shops | Magic Shops CSVs, vetted reusable item candidates |
| `quests` | Campaign Quest Development | Current-region eligible private outlines, quest readiness |
| `estates` | Estate Ledger Updates | Evidence-backed accounting/operations through confirmed campaign time |
| `atlas` | Maintain campaign atlas | Overlay/register, never base map |
| `maintenance` | Campaign Record Maintenance | Provenance, continuity, scoped repair, generated-view checks |
| `sync-repair` | Background Repair Worker; Record Maintenance fallback | Isolated evidence-supported validation repairs, never automatic merge |

The existing daily schedules remain unchanged. The sync-repair PR subscription is configured; consult `sync-repair/IMPLEMENTATION_REPORT.md` for tested delivery status. Runs can be requested explicitly through the available automation controls; they are not launched automatically from an ordinary GitHub push. Never promise that a worker is active until its actual run is confirmed.

## Creating a request (live game)

1. **Do not block the player's game turn.** If work is useful but not needed for the next decision, record the prospective request in the in-conversation unsynced ledger and continue narrating. At the normal campaign sync boundary, or if the player explicitly asks to hand it off now, create **one** immutable JSON file under `automation/handoffs/requests/<lane>/<request_id>.json` in an expected-SHA guarded commit. The handoff itself is meta; it does not require a CAMPAIGN_STATE update.
2. Pick a stable ID such as `HANDOFF-D265-SHOPS-FUTURE-TOWN-CANDIDATES-001`. Before writing, search existing request and result files for the same purpose; reuse existing ID on retries. Do not enqueue a duplicate for the same unresolved scope.
3. Required fields: `request_id`, `lane`, `source` (source.kind, source.checkpoint_id), `request`, `scope` (at least one string), `output_owner_paths`, `priority` (`normal` or `high`), `advances_gameplay: false`. See `TEMPLATE.json`. Include exact prior accepted player limits, no speculative rewards/rolls, and the permissible reference paths. The player does not need to see DM secrets. Note that this is a **public repo**.
4. Do not wait for task completion, repeatedly fetch the queue or poll CI during the gameplay reply. Until committed, the in-conversation request is **not** durable. Once committed, it is pending until a worker's receipt confirms its status. Work required for V's *immediate choice* stays in the live DM conversation; do not pretend an external worker will deliver instantly.

## Worker procedure (scheduled task)

At the start of the existing worker's normal scheduled run, after establishing the authoritative checkpoint, list **only that lane** under `requests/<lane>/`. Compare request IDs with `results/<lane>/`. Process **up to two** outstanding requests in priority/arrival order, within the worker's existing specialist scope and time budget. If a result already says `complete` or `superseded`, skip it. A `blocked` result requires changed evidence or a new explicit request to revisit; `partial` is eligible for bounded resumption from the recorded point, never from invented history.

Confirm each request remains compatible with the **latest** owning evidence and player correction, not the outdated checkpoint recorded when it was queued. Use expected-SHA guarded commits and stable event IDs; only write actual supported changes in the proper owners. **Do not** generate player decisions, force NPC knowledge, consume V resources, roll unplayed encounters, retroactively advance campaign time, spend unauthorized funds, change the base map, or overwrite live DM changes. DM-prep and reusable catalogs can be improved without advancing play.

After verifying real owning changes, write or update only `results/<lane>/<request_id>.json` with `request_id`, `lane`, `status` (`complete`/`partial`/`blocked`/`superseded`), `summary`, `owner_refs`, `verified_commit` where applicable, `blocker` and `next_trigger`. Report completion only if the owner commit was verified. On errors, leave a `blocked` or `partial` receipt with exact unsynced deltas. Do not claim delivery to V or that a playable scene occurred.

## Picking up results

At the next relevant live scene or chat startup, look up **only** receipts tied to the pending action/locale. Read the referenced owning records before using results. An offscreen prepared shop is not a player-known market until V discovers it; an eligible quest is not offered until an NPC actually delivers it during play. A receipt is not authority over later player corrections.

## Safety and reliability

- Preparation lanes use existing schedules. Sync-repair uses the PR event subscription and existing maintenance fallback under `sync-repair/README.md`. Configuration alone does not prove task delivery.
- One request ID, one lane, one result file; never use broad index rewrites as a lock. Multiple workers own different lanes. Guard every repository update against concurrent main changes and retry without duplicating successful event IDs.
- Queue files are operational metadata, not an alternate CAMPAIGN_STATE, SESSION_LOG, personal inventory, shop Stock or estate ledger.
- Do not run unrelated estate, shop, atlas or whole-world audits for a queue entry outside that subsystem.
- Preserve closed/retired queue requests and receipts as audit evidence; archive them in place by scoped maintenance, not in live startup READMEs.
