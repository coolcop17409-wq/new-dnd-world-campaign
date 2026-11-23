# Immutable recovery chunks — v2, GitHub authority

**Live mode:** `automation/recovery/mode.json` is authoritative for storage routing. `mode:"legacy"` means keep the existing `active.json` procedure unchanged. **Do not switch to chunks while any legacy accepted event is unsynchronized**, an accepted-play owner batch is still running, or a live chat is writing the old format.

This is a storage optimization only, never permission for another player action, RNG, resource expense, NPC outcome or game-time passage. Immutable GitHub files are public repository records (DM labels restrict in-game revelation, not access).

## Per-response fast path after a verified v2 cutover

1. Resolve the live turn from verified rules, actual executed dice and independent NPC agency. Preserve the exact original accepted-play event envelope, including `request_id`, `base_commit`, checkpoints, `source_evidence`, `pending_action`, dependencies, and every event's before/after/owner-path fields. Validate using `automation.recovery_chunks.chunk_content` and `automation.recovery_journal.check`.
2. Store **one UTF-8 JSON file only** at `automation/recovery/chunks/D<campaign-day>/<PLAY-REC-D...>.json` (see `chunk_path`) through GitHub `create_file`, guarded by file nonexistence. Its exact JSON is `chunk_content(entry)`. Read the specific file back and compare parsed object and `digest(entry)`. On an identical retry, return success without another commit; on mismatched same ID, reject and retain original; never rename, overwrite or delete accepted chunks. Do not write an index or `active.json` each turn.
3. Keep the verified in-conversation tactical packet. On a new chat, read owner checkpoint and `mode.json`, list only the relevant current-day and later `automation/recovery/chunks/D###/` directories since the last verified owner/checkpoint; check exact entries and reconstruct the unverified suffix through checkpoint/dependency links. **If ordering, coverage or an overlapping prior request is ambiguous, do not infer or replay**: consult verified owner receipts/chunk paths narrowly. Avoid bulk retrieval of closed history.
4. If a GitHub write fails, the action remains accepted in conversation but **not durable** until a verified chunk exists. Report it rather than claiming success or doing an unrelated audit.

## A genuine natural sync boundary

Once the user reaches completed combat/significant exploration, qualifying rest, important transaction/NPC or quest milestone, roughly 8–12 substantive changed exchanges, or explicitly pauses/requests sync:

- Prepare a **single immutable** `automation/recovery/boundaries/<PLAY-...>.json` containing the exact ordered unsynced chunk paths and their `automation.recovery_journal.digest` values, built with `make_boundary`. The initial `source_checkpoint` must equal the currently accepted **owning** checkpoint (or a fully verified prerequisite). Later entries must form a continuous, unambiguous checkpoint chain. Store/read back this boundary with GitHub `create_file`; no guessed latest event or automatic time advance.
- `.github/workflows/immutable-recovery.yml` runs only on a new boundary file, **not** on ordinary chunk files. It loads those files at the immutable boundary commit, checks hashes and identities, and refuses to overwrite any pending `active.json` journal.
- Its background adapter `automation/recovery_chunk_bridge.py` constructs the exact legacy-compatible v1 recovery journal once for that boundary, commits it through the existing non-force guarded writer, then directly uses `automation.auto_sync_submit.submit` to create one deduplicated draft `[CAMPAIGN-SYNC]` PR. It does not rely on a token-generated second Actions push. The established independent Work worker applies owning records/validates CAMPAIGN_STATE last. No auto-merge.
- After a **verified** complete receipt and recovery cleanup, the original chunk files and boundary stay immutable in Git history. A future boundary must use only newer unsynced chunks, not repost an already accepted event. Historical dependencies remain resolved by pinned prior request manifests and verified receipts. A blocked boundary stays available for the maintenance worker to retry by exact ID after resolving the blocker; never delete chunks to force progress.

## Controlled cutover

Requirements **all at once**: (a) verified `[CAMPAIGN-SYNC]` owner/checkpoint receipt and matching generated view; (b) `active.json` has zero entries; (c) no conflicting Work writer or earlier unhandled boundary; (d) latest accepted live chat is at a known recoverable checkpoint; (e) chunk tests and bridge tests passed, and the mode flip uses a guarded current-main write.

Only then set `mode.json` to `{"schema_version":2,"mode":"chunked","activation_checkpoint":"<exact current owner checkpoint>","cutover_commit":"<verified current SHA>"}`. Do not manufacture a recovery entry for activation. Live DMs must use immutable chunks after cutover, not legacy per-turn append; the v1 `active.json` becomes **background compatibility output only**. Existing Project instructions refer to the repository's latest owning procedure.

If the mode is still `legacy`, **v2 is not active**, even if code/README/CI exists. Reverting after new chunks requires verified migration of every outstanding exact entry into the old journal before changing the mode; never just toggle the flag or lose the chunk stream.

## Known limits

Chunking reduces per-response payload size and avoids rewriting a growing file, but does not remove one necessary durable write/readback. Startup after many unsynced turns may require several small chunk reads. A bridge can refuse overlapping batches or unresolved checkpoint history; preserve entries and let maintenance reconcile rather than bypassing checks. Neither the synthetic tests nor staging activation alone prove future live latency.
