# Background synchronization implementation — verification record

Implementation date: 2026-11-20 (America/Los_Angeles). Administrative work only; current played checkpoint unchanged.

## Local verified results

- 30 synchronization/fast-play/handoff tests passed, including synthetic Tarnford 28gp sale/debit/inventory linkage, malformed journal rejection, duplicate/conflicting IDs, nonfinite quantities, expected intermediate checkpoint, final-checkpoint rejection, repair deduplication, terminal receipts, repair/fork event exclusion and scoped market checks.
- 13 existing estate-ledger regression tests passed because the estate workflow's publication guard changed.
- Current character overlay, shop records, final checkpoint and handoff queue passed scoped validation. All seven workflow YAML files parsed.
- One historical OOC market preparation row lacked three empty trailing fields. Padded only those empty cells; no accepted event, money, stock, item, time or character baseline changed.

## Configuration

- Dedicated Work PR task created and enabled: New DnD World — Background Repair Worker.
- Repository/title filters: coolcop17409-wq/new-dnd-world-campaign; `^\[CAMPAIGN-REPAIR\]`.
- Comment/review/commit triggers disabled; prompt handles opened events only.
- Existing Campaign Record Maintenance prompt extended to consume sync-repair as fallback. All five existing schedules preserved.
- Default collector token: GITHUB_TOKEN. Optional repository-scoped CAMPAIGN_REPAIR_TOKEN only if owner-authorized credentials are needed.

## Remote integration status

Pending initial publication and live synthetic test. A configured Work task is NOT proof of GitHub-to-Work delivery. No end-to-end success is claimed here. Subsequent verification will record actual run/commit/PR identifiers and remaining blockers. Synthetic rows belong only to isolated fixtures/test branches; they must never merge to main.

## Known boundaries

Local tests demonstrate schema/bounds/idempotency and policy contracts, not arbitrary semantic truth in player prose or measured future DM latency. Prepublication checks are effective when callers use the documented preflight; GitHub Actions otherwise detects errors after push. An account-level protected-branch rule is needed to enforce PR-only preflight against all writers. Unsynced conversation deltas cannot be recovered by a worker that never received them. Background repair proposals require verification and a separately authorized merge; no repair auto-merges.
