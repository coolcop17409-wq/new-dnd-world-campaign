# Verified in-conversation scene cache specification

This is a **cache, not canon**. Keep one current scene packet in conversation; `runtime/SCENE_CACHE.md` is the last explicitly grounded quickstart snapshot and might lag newer chunked gameplay. Never overwrite owning state or the original immutable recovery.

## Required packet fields
- `owner_checkpoint_id`, `latest_played_event_id`, `campaign_day/local_time`, `scene_id`, current pending V action and evidence/authority status.
- `source_pins`: file path, revision (blob SHA when known), exact section/owner, classification (`accepted owner`, `newer accepted recovery`, `DM-only preparation`, `proposal`, `unverified`), and who is allowed to know it.
- `party`: V/Mara/Cirren/Fenar actual location, initiative/turn if in combat, HP/AC/slots/finite resources, equipment custody, timed effects and conditions; never use stale dashboard over newer recovery.
- `actors`: identity, current location, independently established motives, what each **actually knows** (witness/official/hearsay), relationships, offers and likely self-preserving behavior; no omniscience.
- `tactics`: threat identity/source and printed 2014 mechanics; exact positions, visibility/cover, surprise/reactions, concentration, conditions, remaining HP, timers, state of retreat/surrender, genuine executed rolls. Only for current combat.
- `quest_delivery`: 2–4 **eligible** leads with source/status (unintroduced/offered/accepted/declined/resolved), conditions, independent clocks and restrictions. Preparation does not count as played.
- `recovery_cursor`: latest verified owner event and ordered unsynced chunk IDs/checkpoints. Do not treat worker-created compatibility `active.json` as current chunk cursor.
- `unknowns`: contested measurements, supplies/permissions, unspecified NPC knowledge or unplayed facts. Flag, do not silently fill in.

## Trigger → minimal refresh (not blanket reload)
| Trigger | Read / action |
| --- | --- |
| Another attack in **same** encounter | Update retained round/HP/effects; no monster/rules lookup unless missing, conflicting or new feature |
| New opponent/condition/spell | Relevant source + owning rules subsection, one-time pin |
| Established NPC speaks | Actor's retained motive/knowledge; no repeated NPCS download if unchanged |
| First prominent new NPC/faction, major secret/document | Relevant owning NPC/DM-only/quest/political subsection and established evidence; preserve private/public divide |
| Enter new locale/region; substantial journey | Scoped regional atlas/quest prep/travel RULES; verify real elapsed time/encounter rules; no pre-rolling |
| Actual rest, resource spend, permanent custody change | Scoped rest/resource/inventory RULES and changed event/owner |
| New player correction, conflict or later accepted chunk | Overwrite **only** disputed cache fields from higher authority; pin actual correction |
| Verified owner checkpoint/region prep update | Invalidate changed source pins only; do not restart a known combat |
| Routine low-risk movement/dialogue | Keep existing packet; record changed outcome in one immutable chunk |
| Meaningful scene transition | One-time quest delivery/visual preflight where prescribed; no repetitive whole-source audit |

## Validation discipline
- A cached value must have a source and a **last-known revision** or be clearly marked in-conversation accepted recovery.
- A public NPC cannot cite DM-only facts unless that NPC learned them through a supported route/time.
- "No known threat" is not "the region is safe"; "prepared" is not "offered" or "accepted."
- When conflict changes a decision or combat mechanic, fetch the narrow authority before adjudicating that fact.
- The DM uses the latest accepted in-conversation tactical packet across ordinary turns. On new chats, reconstruct from owner checkpoint plus immutable recovery suffix and the currently applicable scoped prep; do not assume this persisted cache is current.
- No extra per-turn GitHub write is created for packet updates. Only the accepted-play recovery chunk is written immediately.
