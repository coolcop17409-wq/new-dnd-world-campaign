# Per-response recovery journal

Owner authorized 2026-11-21. `automation/recovery/active.json` on main is the durable buffer of accepted play not yet verified in owning records. This narrowly supersedes older no-per-turn-write instructions. It is evidence for recovery, not another resource ledger or permission to adjudicate. No new automation or per-turn PR is needed.

## Capture while responding

For each response with new accepted play, rolls, facts, explicit corrections, time/resource/custody changes or a changed pending decision, append one entry BEFORE finishing the response. Do not write for unchanged discussion. Use the `accepted_play` envelope schema from `automation/play_handoff.py`: a stable unique `PLAY-REC-<session>-<sequence>` request_id, exact base_commit, source/destination checkpoint, source_evidence, pending_action, depends_on and events. Each event has stable event_id, accepted=true, exact evidence/before/after and owner_paths. Include the precise tactical state needed to continue, actual executed dice and relevant verbatim player instructions. No invented missing values; no proposed V decisions. A record captures already resolved authorized outcomes, not an unapproved proposal. Corrections get a new event and explicitly identify what they supersede; never mutate old entries.

Read current main head and active.json (retain blob SHA). Check the existing campaign writer slot; respect active writer locks. Validate and append with current-main helper, or follow identical checks if execution is unavailable. Publish only active.json via create_tree → create_commit(parent=expected main) → update_ref(expected_sha=expected, force=false); read back exact contents. A stale expected SHA requires reread/reconciliation, never blind overwrite. Identical entry retries are no-ops; conflicting IDs block. Never reuse a previously submitted event ID for a different outcome, even after cleanup. Consult immutable requests/receipts on recovery or uncertain retries.

Commands (run from repository root; outputs are proposed files, never direct GitHub writes):

```
python3 -m automation.recovery_journal validate automation/recovery/active.json
python3 -m automation.recovery_journal append automation/recovery/active.json --entry /tmp/entry.json
```

Say **recovery recorded** only after readback; this is not **queued** or **saved to owners**. If capture fails, say **recovery write failed; latest changes remain unsaved**, retain the delta and retry stable IDs on the next response. Do not silently advance dependent mechanics after an ambiguous concurrent conflict. There is no capture after a response ends, or guaranteed write on abrupt interruption. Keep all unverified entries even if the buffer grows; never trim for size alone. Appends do not rebuild dashboards, run estate audits, create PRs or wait for background work.

## Normal batch handoff

At existing sync boundaries, freeze a snapshot of eligible entries into the existing immutable `[CAMPAIGN-SYNC]` request. Preserve each event object/ID exactly, in causal order; include complete evidence and final pending action. The request's source/destination checkpoints span the selected entries. Add `recovery_entries`, an object mapping each selected recovery request_id to its canonical SHA-256 (`digest(entry)` in the helper). Dependencies remain explicit. Search existing requests before resubmitting events; reuse the same transport on retry. Entries already queued stay in the buffer but must not be submitted in a second batch. New responses continue appending during application. No change to opened-only dispatch, claims, scoped tests, owner verification, checkpoint-last or no-auto-merge rules.

## Startup and interrupted chat recovery

After reading current owning checkpoint, read active.json and pending play-sync requests/results before resuming. Compare exact evidence and stable IDs with current owners and immutable queued requests; distinguish recorded-only, queued, partially applied and fully verified. Recover the latest supported pending decision without replaying actions, dice or resource deltas. Preserve later player corrections and newer owners; block ambiguous dependent mechanics. Foreground chat may submit unqueued recovery entries through the normal existing handoff protocol once reconciled. Maintenance/worker must not recursively create PRs/tasks; they consume existing requests and may clean verified entries. Recorded-only entries remain durable for next-chat submission, not automatically delivered to a worker.

## Cleanup after verified application

The worker (or next foreground/maintenance reader) may prune only after fetching the immutable request, central main result and actual owner/checkpoint refs and independently verifying the batch's effects. Never trust PR prose, queued/partial/blocked results or claimed IDs alone. Smoke tests never prune. Missing evidence means retain, not delete. Generated-view failure alone does not invalidate verified owning changes; report derived-pending separately.

A cleanup-capable central receipt includes status=complete, request_id, `request_digest=digest(entire immutable request)`, owners_verified=true, owner_commit, tested_commit, tests=[{command,exit_code:0}], owner_refs (nonempty exact GitHub file/commit references), and verified_event_ids. Include both newly applied and identical already-recorded IDs only after source comparison. Changed checkpoints additionally require checkpoint_commit and checkpoint_verified=true. Older receipts lacking these bindings require fresh independent verification and a guarded receipt update before cleanup.

```
python3 -m automation.recovery_journal prune automation/recovery/active.json --request /tmp/request.json --receipt /tmp/verified-result.json
```

This helper validates bindings; it cannot verify remote truth. Fetch latest active.json immediately before pruning, run the helper, and publish its output with expected-main-SHA protection. Delete only fully covered entries with matching hashes and exact event contents. Preserve newer/unsubmitted/unverified entries. On a concurrency failure, reread and recompute. Cleanup is a separate administrative commit AFTER the complete result, never part of owner/checkpoint application. If interrupted, it is safe to retry; already absent entries are no-ops. When all are covered, retain the empty JSON container. Git history and immutable requests preserve the removed evidence. No gameplay, owner or checkpoint write is performed by cleanup.
