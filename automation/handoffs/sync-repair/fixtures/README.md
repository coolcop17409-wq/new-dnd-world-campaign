# Isolated synthetic integration test

This is NOT a played campaign event. This branch must never merge into main. The expected fixture represents a synthetic 28gp debit only for schema testing; no live personal money changes.

Intentional defect: integration-character.csv has one EXTRA EMPTY TRAILING FIELD on its single data row (10 columns instead of the 9-column Character Events schema). The sole authorized correction is to remove that final extra comma, leaving every value unchanged. Preserve the header, stable test ID, -2800 delta, evidence and posted status. Do not post this fixture to any live journal.

Run `python3 automation/handoffs/sync-repair/check_fixture.py` after the correction, then `python3 -m unittest automation.test_sync_repair automation.test_fast_play automation.handoffs.test_validate -v`. Record actual commands/results and tested SHA in separate verification/result receipts. Keep the repair PR draft, targeting this campaign-sync-test branch. Do not merge automatically. The original failing run must remain as evidence; do not claim a manual task run verifies automatic webhook delivery.
