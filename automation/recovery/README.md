# Per-response recovery journal

Owner authorized 2026-11-21. `automation/recovery/active.json` on main is the durable buffer of accepted play not yet verified in owning records. This narrowly supersedes older no-per-turn-write instructions. It is evidence for recovery, not another resource ledger or permission to adjudicate. No new automation or per-turn PR is needed.

## Capture while responding

For each response with new accepted play, rolls, facts, explicit corrections, time/resource/custody changes or a changed pending decision, append one entry BEFORE finishing the response. Do not write for unchanged discussion. Use the `accepted_play` envelope schema from `automation/play_handoff.py`: a stable unique `PLAY-REC-<session>-<sequence>` request_id, exact base_commit, source/destination checkpoint, source_evidence, pending_action, depends_on and events. Each event has stable event_id, accepted=true, exact evidence/before/after and owner_paths. Include the precise tactical state needed to continue, actual executed dice and relevant verbatim player instructions. No invented missing values; no proposed V decisions. A record captures already resolved authorized outcomes, not an unapproved proposal. Corrections get a new event and explicitly identify what they supersede; never mutate old entries.

**Fast append (mandatory during combat):** Retain the latest verified recovery journal and its blob SHA in the conversation. If unavailable, call GitHub `fetch_file` for `automation/recovery/active.json` once; establish the source/base campaign checkpoint from the retained verified scene, not an unrelated full repository scan. Prepare a valid new entry; use `automation.recovery_journal.append` (or the equivalent exact schema/idempotency checks) **locally**. Write the complete updated JSON through GitHub `update_file` with `path="automation/recovery/active.json"`, the existing **blob SHA** (`sha`), and `branch="main"`. GitHub's Contents API rejects a changed file blob SHA (optimistic concurrency); this is an owner-authorized alternative for this **one independent metadata file only** to the create_tree → create_commit → update_ref multi-call path. Do not use this shortcut for owning journals, generated views, or CAMPAIGN_STATE.

Read back **only** `automation/recovery/active.json` once (preferably at returned commit SHA) and verify exact appended entry/ID/evidence. Identical retries are no-ops; on conflicting changed SHA, refetch only this file, validate/reconcile existing IDs, and retry the same stable event once without overwriting another writer's entry. If still blocked, retain the unsaved delta and disclose failure; do not enter a multi-minute retry or GitHub Actions diagnostic loop. Recovery-only file edits do not require an owning-record writer lease, but must respect any explicit global repository write freeze. Never recheck unchanged monster stats, full character/quest trackers, GitHub workflows or unrelated owner files as part of this append.

Target concise evidence without losing crucial die faces, actions, positions, effects, resources, source/target checkpoints or exact player instruction. Avoid duplicating long narrative in source_evidence, event evidence, before and after; preserve each field's required factual meaning. No arbitrary truncation of accepted evidence. Never reuse a submitted event ID for a different outcome, even after verified cleanup. Consult immutable requests/receipts only on startup, uncertain retries, or actual batch submission—not every unchanged combat turn.

Commands (run from repository root; outputs are proposed files, never direct GitHub writes):

```
python3 -m automation.recovery_journal validate automation/recovery/active.json
python3 -m automation.recovery_journal append automation/recovery/active.json --entry /tmp/entry.json
```

Say **recovery recorded** only after readback; this is not **queued** or **saved to owners**. If capture fails, say **recovery write failed; latest changes remain unsaved**, retain the delta and retry stable IDs on the next response. Do not silently advance dependent mechanics after an ambiguous concurrent conflict. There is no capture after a response ends, or guaranteed write on abrupt interruption. Keep all unverified entries even if the buffer grows; never trim for size alone. Appends do not rebuild dashboards, run estate audits, create PRs or wait for background work. **Do not poll CI or inspect full owner state after a successful fast append.**

## Normal batch handoff

At existing sync boundaries, the committed accumulating journal is the REQUIRED source of new sync batches. Do not reconstruct, supplement or summarize missing events from chat at submission time. First record any missing accepted evidence or explicit corrections through the guarded append procedure and read it back. If the journal lacks sufficient evidence, retain/block the batch; do not infer it. Existing pre-change immutable transports remain valid under their original protocol; smoke tests remain separate.

Fetch active.json at an exact main commit (retain Git blob SHA and establish that commit belongs to main history). Search open AND closed play-sync PRs and durable requests, including abandoned transports, for relevant request/event IDs; paginate and fetch exact immutable request files. Reconcile their central results and any partial owner phases. Supply the complete relevant accepted-play requests as a JSON array to the builder; an empty array means a verified empty queue/history for these IDs, not a skipped search. The builder is offline and cannot certify discovery completeness. Reuse an existing exact batch ID/request on retry; never rebuild it from a later journal. Conflicting/partial overlaps need reconciliation, not another transport.

```
python3 -m automation.recovery_batch build /tmp/pinned-active.json --journal-commit <exact-main-SHA> --request-id PLAY-<checkpoint>-<sequence> --prior-requests /tmp/prior-requests.json
```

Use the output unchanged as the immutable existing-lane request. It selects all unqueued entries in causal order, copies event objects exactly, concatenates their stored evidence, takes the first source/base and last destination/pending decision, and resolves dependencies on queued batches. It pins the full journal snapshot and per-entry hashes. Empty journals/no unqueued entries produce no request. Checkpoint gaps, forward/unresolved dependencies, altered duplicate IDs and partial overlaps fail closed. Stable IDs and original entry base commits remain available in the pinned journal. No full owner sync is performed by the builder.

Before claiming/applying, the worker fetches the journal at request.journal_source.commit from main history and the immutable prior_request_ids, verifies its content against the pinned digest and independently checks current owners/newer corrections. Run trusted current-main code:

```
python3 -m automation.recovery_batch verify /tmp/pinned-active.json --request /tmp/request.json --prior-requests /tmp/prior-requests.json
```

The whole generated request must match exactly, including pending action, evidence, dependencies and ordered events. Never execute request-branch code. Later appends do not alter the frozen batch. Continue using existing opened-only transport, central claims, expected-SHA guards, scoped tests, owner verification and checkpoint-last publication. Keep entries until verified cleanup; do not queue their events twice. The foreground submits at existing boundaries; no new timer, watcher, per-turn PR or task is created.

## Startup and interrupted chat recovery

After reading current owning checkpoint, read active.json and pending play-sync requests/results before resuming. Compare exact evidence and stable IDs with current owners and immutable queued requests; distinguish recorded-only, queued, partially applied and fully verified. Recover the latest supported pending decision without replaying actions, dice or resource deltas. Preserve later player corrections and newer owners; block ambiguous dependent mechanics. Foreground chat may submit unqueued recovery entries through the normal existing handoff protocol once reconciled. Maintenance/worker must not recursively create PRs/tasks; they consume existing requests and may clean verified entries. Recorded-only entries remain durable for next-chat submission, not automatically delivered to a worker.

## Cleanup after verified application

The worker (or next foreground/maintenance reader) may prune only after fetching the immutable request, central main result and actual owner/checkpoint refs and independently verifying the batch's effects. Never trust PR prose, queued/partial/blocked results or claimed IDs alone. Smoke tests never prune. Missing evidence means retain, not delete. Generated-view failure alone does not invalidate verified owning changes; report derived-pending separately.

A cleanup-capable central receipt includes status=complete, request_id, `request_digest=digest(entire immutable request)`, owners_verified=true, owner_commit, tested_commit, tests=[{command,exit_code:0}], owner_refs (nonempty exact GitHub file/commit references), and verified_event_ids. Include both newly applied and identical already-recorded IDs only after source comparison. Changed checkpoints additionally require checkpoint_commit and checkpoint_verified=true. Older receipts lacking these bindings require fresh independent verification and a guarded receipt update before cleanup.

```
python3 -m automation.recovery_journal prune automation/recovery/active.json --request /tmp/request.json --receipt /tmp/verified-result.json
```

This helper validates bindings; it cannot verify remote truth. Fetch latest active.json immediately before pruning, run the helper, and publish its output with expected-main-SHA protection. Delete only fully covered entries with matching hashes and exact event contents. Preserve newer/unsubmitted/unverified entries. On a concurrency failure, reread and recompute. Cleanup is a separate administrative commit AFTER the complete result, never part of owner/checkpoint application. If interrupted, it is safe to retry; already absent entries are no-ops. When all are covered, retain the empty JSON container. Git history and immutable requests preserve the removed evidence. No gameplay, owner or checkpoint write is performed by cleanup.
