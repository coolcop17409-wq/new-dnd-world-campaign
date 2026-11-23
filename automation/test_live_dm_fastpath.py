import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(path):return (ROOT/path).read_text(encoding="utf-8")
class LiveDMContractTests(unittest.TestCase):
    def test_startup_contract_has_one_chunked_recovery_route(self):
        for p in ("README.md","AGENTS.md","campaign/continuity/readme.md"):
            txt=read(p)
            self.assertIn("runtime/LIVE_DM_FAST_PATH.md",txt)
            self.assertIn("immutable",txt.lower())
        self.assertIn("create_file",read("runtime/LIVE_DM_FAST_PATH.md"))
        self.assertIn("one immutable",read("AGENTS.md").lower())
        self.assertNotIn("do not perform GitHub writing",read("AGENTS.md"))
        self.assertNotIn("Each response with new accepted play appends exactly one guarded recovery entry in",read("campaign/continuity/readme.md"))
    def test_cache_cannot_outrank_owners_or_newer_chunks(self):
        cache=read("runtime/SCENE_CACHE_SPEC.md")
        self.assertIn("not canon",cache.lower())
        self.assertIn("immutable",cache.lower())
        self.assertIn("source_pins",cache)
        self.assertIn("NPC",cache)
        self.assertIn("Invalidate",cache)
    def test_source_router_does_not_replace_rules(self):
        index=read("runtime/SCOPED_RULES_INDEX.md")
        for required in ("rules-combat-recovery.md","rules-dm-procedures.md","rules-travel-communication.md","rules-quest-design.md"):
            self.assertIn(required,index)
        self.assertIn("remain authoritative",index)
    def test_region_brief_still_distinguishes_play_and_prep(self):
        brief=read("runtime/REGION_PREP.md")
        self.assertIn("Sedgecross",brief)
        self.assertIn("not accepted",brief.lower())
        self.assertIn("D282",brief)
        self.assertIn("immutable",brief.lower())
    def test_optional_diagnostics_only_metadata(self):
        code=read("automation/fastplay_diagnostics.py")
        self.assertIn("explicit_user_or_local_tool_trace_only",code)
        self.assertIn("source_evidence",code)
        self.assertNotIn("requests.get(",code)
