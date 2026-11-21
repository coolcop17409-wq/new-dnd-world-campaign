# Background synchronization — implementation and verified boundaries

Administrative implementation dated 2026-11-20 America/Los_Angeles (remote runs crossed midnight into November 21). Accepted campaign-state, session-log, character event journal and all three character baselines are unchanged from initial source commit `a6bb82648b13158325f0f3335f9c53cbb1d05daf`. One historical OOC market row was padded with three omitted empty trailing fields; no values/effects changed. A concurrent atlas publication was preserved.

## Active implementation

| Component | Behavior |
| --- | --- |
| Character journal workflow | Strict owning schema, stable IDs, finite integer deltas, evidence and resource/inventory replay; owner-first intermediate commits permitted |
| Magic-shop workflow | Shop-only schema, identity and quantity checks; no estate/Blackthorn/tax replay |
| Final fast-play workflow | Exact newest-event/checkpoint reconciliation, character overlay, then dashboard/PLAY_NOW generation |
| Estate workflow | Existing estate scope/schedule preserved; defers generated packet during expected log-before-final-checkpoint interval |
| Generated publication | Exact source head must still be current; no rebase or force push over newer owners |
| Repair collector | Trusted main code, bounded diagnostics, stable failure signature, durable existing-queue request, deterministic repair branch/draft PR, retries/dedup, current-source resolution check |
| Work worker | PR title filter `^\[CAMPAIGN-REPAIR\]`; opened events only in prompt; comment/review/commit triggers disabled; independent guarded correction/test/receipt, never merge |
| Scheduled fallback | Existing Campaign Record Maintenance consumes same repair queue and resumes missing PR creation; all five original schedules verified unchanged and enabled |

Collector permissions: Contents write, Pull requests write, Actions read. Repair/fork/PR-origin failures are excluded before collection; per-original-run concurrency avoids irrelevant runs cancelling eligible collection. Collector errors retain a separate artifact receipt and cannot recursively trigger collection.

## Commits and pull requests

- [Implementation PR #1](https://github.com/coolcop17409-wq/new-dnd-world-campaign/pull/1), implementation `95da3c64bfe14792549baba1093945ed8d071bf1`, merged after five passing GitHub PR checks as `f1614c60c40b25802c7995b39750f8b9cf382ff9`.
- [Artifact redirect correction PR #2](https://github.com/coolcop17409-wq/new-dnd-world-campaign/pull/2), implementation `b2dec78f1fe20a655fadb65bb6773c85b33c4233`, merged after three passing PR checks as `6056f5de5bd3fefe8f50eaf95a4c24140b9325cd`.
- [ID/checkpoint/concurrency correction PR #4](https://github.com/coolcop17409-wq/new-dnd-world-campaign/pull/4), commits `202b8c783dce0a3b21f040ee8a082f012898833b` and `b368cb57b260cadc6ae48e60cec1688ef029161d`, merged after three passing PR checks as `342dc9c81b9a70a16695a6a6946ee0f5182de2a9`.
- [Synthetic repair PR #3](https://github.com/coolcop17409-wq/new-dnd-world-campaign/pull/3) remains **draft and unmerged**, targeting `campaign-sync-test/background-repair-20261120`, never main. Worker claim `96d5f2e319d7b36812b403193c848c0f2bdb3635`, actual fixture-only correction `70c86e8f7caa890c6adb05b5a43b105522a102f2`, verification/result receipts `13fa317a1ddba304078bfe9302b154292f4487aa`.
- Synthetic source `9db9ee72d61664f46d6be056d69288b6c3989b95`; durable request created by Actions in `23fdec59b3befa7794b8feab17439e246a2ed940`; initial repair branch marker `4bfa5259165048e1dc110376a02928bce429f1bb`. Test infrastructure compatibility commits `619850b01e78804b39103826746038330a47895b` and `41fb1629357fcc73fed311e6078903ebcc3cf39d` did not change campaign owners. Repeated-failure probe `677ccc69d890781ae4472c1560954ea0306dc963` changed only test documentation.
- Generated refreshes `8cd1124bb5b99b3bdb7385f3ac43fc558ae0b363` and `e0bc5ef1fbca43a50b05abcdfece826015e63817` contain derived report changes only.

## Tests and live evidence

Final local command: `python3 -m unittest automation.test_sync_repair automation.test_fast_play automation.handoffs.test_validate automation.test_estate_ledger -q` — **47 passed**. Current final checkpoint/character overlay and shop-only checks also pass. All workflow YAML parses. Separate real local-git concurrency exercise confirmed a stale generated writer leaves a concurrent newer owner intact and publishes no stale view.

| Requested case | Actual result |
| --- | --- |
| Valid event creates no repair | PASS: preflight and production validation passed; success collectors skipped |
| Invalid event produces one diagnostic | PASS: isolated fixture failed with one csv.width finding; original [run 44883407405](https://github.com/coolcop17409-wq/new-dnd-world-campaign/actions/runs/44883407405) |
| Duplicate failures do not duplicate requests/PRs | PASS: repeated unchanged failure [44883967889](https://github.com/coolcop17409-wq/new-dnd-world-campaign/actions/runs/44883967889); collector [44883987053](https://github.com/coolcop17409-wq/new-dnd-world-campaign/actions/runs/44883987053) returned existing_pr and the same request/PR #3. One request file and one repair PR confirmed |
| Draft repair PR created | PASS via connected GitHub after Actions was denied PR creation; automatic Actions creation remains blocked |
| PR event starts separate Work task | PASS for connector-created PR #3, opened webhook delivery `1311e7a6-e583-11f1-9db7-696285c910b9` |
| Independent worker commits safe fix | PASS: removed only extra trailing comma in synthetic fixture; live owner journals untouched |
| Validation passes after correction | PASS: worker executed fixture check, 30 branch-version regression tests and handoff validation; GitHub PR checks [44883856746](https://github.com/coolcop17409-wq/new-dnd-world-campaign/actions/runs/44883856746), 44883856749 and 44883856701 all passed |
| Concurrent changes protected | PASS: independent worker hit a moved head, reread and preserved concurrent validator commit before guarded retry; separate real-git publication test also passed |
| Repair updates do not create loops | PASS: excluded repair/PR branches; subsequent fix/receipt commits did not create another Work run/request/PR |
| Live narration independent | Implemented policy and architecture: no CI/repair wait on routine turns, worker is a distinct completed task. No new gameplay was performed to measure player-turn latency |
| Log precedes final checkpoint | PASS: owners phase returns PENDING_CHECKPOINT; final phase rejects mismatch; reconciled final passes |
| Tarnford Rope of Mending | PASS synthetic: SALE in Magic Shops, -2800cp in Character Events, inventory_create qty1 overlay with JSON custody/source, stable linked IDs; replay produces exactly one rope and one 28gp debit; duplicate/malformed/missing/wrong-amount legs rejected |

Work run `47f6c885-3570-8325-8a8a-2d12d8b81019` started 2026-11-21 08:11:00Z and completed 08:13:46Z. Recorded result confirms the correction, actual tests and unmerged draft. [Separate worker conversation](https://chatgpt.com/c/6b014f07-0680-83e8-9468-b03589138113). This was an actual PR-triggered run, **not run_now or a local subagent**.

## Failures encountered and resolved

- First collector attempt: HTTP 401 on artifact storage redirect. Fixed credential stripping on cross-host HTTPS redirects, rejected HTTP redirects, added regression test, preserved failure receipts. Subsequent artifact retrieval and durable queue writes succeeded.
- Original handoff validator rejected generated repair IDs. Fixed only the dedicated signature form and tested collector output with the real queue validator. Current handoff checks pass.
- Global workflow concurrency allowed irrelevant runs to replace pending collection. Moved filtering/concurrency to eligible jobs keyed by original run ID. Repeated-failure collection subsequently succeeded.
- The malformed fixture intentionally remains invalid on the isolated **test base**; those failed runs are expected negative-test evidence. The repair head passes. Never merge the test branch into main.

## Remaining account-level blocker and precise next action

**The complete Actions → PR → Work path is not verified/operational yet.** GITHUB_TOKEN successfully created the request and repair branch, but POST /pulls returned HTTP 403 in collector [44883422731](https://github.com/coolcop17409-wq/new-dnd-world-campaign/actions/runs/44883422731), attempt 2. The browser was signed out and could not access repository settings; the connected tools do not expose the needed administration setting.

Owner action: in [repository Settings → Actions → General](https://github.com/coolcop17409-wq/new-dnd-world-campaign/settings/actions), under Workflow permissions, allow GitHub Actions to create and approve pull requests, then save. Keep general token defaults unchanged; this workflow requests only its explicit scopes. [GitHub's setting documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository) explains the control. No workflow in this implementation approves or merges PRs.

After that setting is confirmed, test a fresh distinct synthetic failure signature so an **Actions-created** PR opens and starts Work. Reusing PR #3 only verifies dedup, not a new opened event. If bot-origin delivery is still unavailable, supply an owner-authorized repository-scoped GitHub App mechanism or fine-grained token as CAMPAIGN_REPAIR_TOKEN (Contents/Pull requests write; Actions read) and retest. No credentials were requested, created or stored during this implementation.

Until then, durable requests remain available to the existing daily Record Maintenance fallback, which can open the missing PR with the connected GitHub tool and use the same worker/claim/receipts. This fallback is configured at its unchanged 07:00 America/Los_Angeles schedule; its next scheduled consumption has not been observed in this implementation session.

## Other limits

Preflight rejects malformed candidate data before publication when callers actually use it; post-push Actions alone cannot prevent all direct writes. Required protected-branch checks would be separate account-level enforcement. An initial natural-boundary owner/handoff write still must succeed to make chat deltas durable; no worker can recover unposted conversation text. In the same chat, verified accepted facts outrank delayed generated views. If an unresolved discrepancy affects an immediate combat mechanic, hold only that mechanic pending narrow source verification. No semantic assertion, unplayed outcome or future DM latency is declared tested merely because code passes.
