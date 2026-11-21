# Isolated synthetic trigger and repair test — November 21, 2026

This branch exists ONLY to prove the automatic chain:
GitHub Actions validation failure → automated diagnostic repair request → GITHUB_TOKEN-created draft PR → independently triggered ChatGPT Work worker.

Never merge this test base or its repair PR into main. No campaign character resource, recorded play, dice, state or inventory changes are authorized.

The deliberately malformed `integration-character.csv` has exactly nine columns and one isolated synthetic event row with an invalid `status` value `staged`. The actual character-event schema only allows **posted** accepted changes in this journal. Its synthetic event ID is `TEST-ACTIONS-PR-RETEST-20261121-001`. This is NOT an actual player expenditure.

**Permitted isolated repair**: change only the synthetic row status `staged` to `posted`. Preserve all other text (the nine-column header, event ID, date, owner, event type, target, -2800 test delta and evidence). Test `python3 automation/handoffs/sync-repair/check_fixture.py` and `python3 -m unittest automation.test_sync_repair automation.test_fast_play automation.handoffs.test_validate -v`. Do not apply this event to live `data/characters/events.csv` or any owning record.

Record the triggering workflow and draft PR, verify that PR was **created by GitHub Actions** rather than connector tool, and that a separate Work task was actually triggered from the newly opened PR. A created PR alone is not proof the Work task ran; a Work task run alone is not proof Actions created its PR.
