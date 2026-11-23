# Live-play performance baseline and measurement protocol

## Observed baseline (screenshots supplied by player, November 23, 2026)
These are **visible elapsed durations**, not instrumented internal tool traces. No breakdown of hidden reasoning, GitHub connector latency, code execution, generated narration or app overhead is available from screenshots alone.

| Representative request | UI duration observed | Grounded context |
| --- | --- | --- |
| Investigate Kestrel vault, take evidence/loot | **6m 19s** | Major discovery, physical evidence/loot, recovery chunk and milestone boundary |
| Leave Kestrel quickly and quietly | **4m 8s** | Known-route exfiltration, NPC independence and patient reunion |
| Farm Short Rest then Sedgecross | **7m 26s** | Rest/homebrew, genuine rolls, travel and conditional care contact |

The screenshots show extensive work steps, but not every GitHub read/write nor thinking time. **Do not assert these durations were caused by a specific tool or that a shorter model would preserve campaign fidelity.**

## Future comparison (no extra per-turn GitHub commits)
Collect **three to five comparable turns**, preferably one ordinary exchange, established combat action, social conversation, substantial discovery, and time/rest travel. In a diagnostic-enabled session, optionally track *metadata only* in conversation (not another GitHub file): turn ID, start/end wall-clock milliseconds measured by the client when possible, each GitHub read path/revision/bytes, one per-response recovery create + readback, significant source lookup, dice execution and any foreground CI polling. Do not include verbatim private NPC material, player statements, rules text, passwords, DM secrets or source contents in traces.

Analyze explicitly provided metadata with:
`python3 -m automation.fastplay_diagnostics --jsonl <local-trace.jsonl>`.
The script reports observed elapsed time (or null if unmeasured), number of unique/repeated same-revision reads, total read bytes, write/readback count and unnecessary CI polling. It **does not intercept ChatGPT tools automatically** and cannot measure another chat's hidden processing without a real trace. Do not create per-turn telemetry GitHub commits or more background tasks just to measure the benchmark.

## Criteria
- Every gameplay-changing reply still has **one verified immutable recovery chunk**; missing readbacks remain a safety regression.
- No repeat read of the same unchanged source during one scene unless materially needed for conflict.
- New lore/quest/NPC/monster requires relevant source verification, not guessed or skipped detail.
- No owner/migration/estate/market/atlas audit or workflow polling as a precondition of a routine turn.
- Tactical correctness, actual rolls, scenario agency, player spending boundaries and quest continuity must remain unchanged.
- Compare the actual measured durations by scenario type; no unsupported percentage improvement claim.
