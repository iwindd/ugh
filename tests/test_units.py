import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ugh_cloud", PLUGIN / "__init__.py", submodule_search_locations=[str(PLUGIN)]
)
module = importlib.util.module_from_spec(spec)
sys.modules["ugh_cloud"] = module
spec.loader.exec_module(module)

from ugh_cloud.command import handle_ugh
from ugh_cloud.config import agent_name, exclusions, repository, skill_root
from ugh_cloud.domain.planning import action_for, git_blob_sha
from ugh_cloud.skills.discovery import all_skills, find_skill
from ugh_cloud.skills.safety import excluded, suspicious_files
from ugh_cloud.skills.snapshot import files


class Context:
    profile_name = "lyla"

    def __init__(self, home, values=None):
        self.hermes_home = str(home)
        self.values = values or {"github-repo": "iwindd/ugh", "agent-name": "Lyla", "exclude": []}

    def get_config(self, key, default=None):
        return self.values.get(key, default)


class ModularFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name) / "skills"
        (self.root / "productivity" / "report" / "references").mkdir(parents=True)
        (self.root / "productivity" / "report" / "SKILL.md").write_text("report", encoding="utf-8")
        (self.root / "productivity" / "report" / "references" / "guide.md").write_text("guide", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_config_resolves_active_profile_settings(self):
        ctx = Context(self.root.parent)
        self.assertEqual(skill_root(ctx), self.root.parent / "skills")
        self.assertEqual(repository(ctx), "iwindd/ugh")
        self.assertEqual(agent_name(ctx), "Lyla")
        self.assertEqual(exclusions(ctx), [])

    def test_discovery_preserves_category_and_complete_snapshot(self):
        found_id, found_path = find_skill(self.root, "report")
        self.assertEqual(found_id, "productivity/report")
        self.assertEqual(found_path, self.root / "productivity" / "report")
        self.assertEqual(all_skills(self.root), [("productivity/report", found_path)])
        self.assertEqual(files(found_path), {"SKILL.md": b"report", "references/guide.md": b"guide"})

    def test_ambiguous_simple_id_requires_qualified_id(self):
        second = self.root / "software-development" / "report"
        second.mkdir(parents=True)
        (second / "SKILL.md").write_text("other", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "multiple skills found"):
            find_skill(self.root, "report")

    def test_discovery_rejects_traversal(self):
        with self.assertRaisesRegex(ValueError, "category/skill"):
            find_skill(self.root, "../report")

    def test_snapshot_requires_skill_md_and_rejects_symlinks(self):
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaisesRegex(RuntimeError, "SKILL.md"):
            files(empty)

    def test_safety_matches_exclusions_and_secret_names(self):
        self.assertTrue(excluded("private/report", ["private/*"]))
        self.assertFalse(excluded("public/report", ["private/*"]))
        self.assertEqual(suspicious_files({"SKILL.md": b"ok", ".env": b"TOKEN=x"}), [".env"])

    def test_planning_covers_add_patch_noop_and_remove(self):
        local = {"SKILL.md": b"hello"}
        sha = git_blob_sha(b"hello")
        self.assertEqual(action_for(local, {}), "add")
        self.assertEqual(action_for(local, {"SKILL.md": "different"}), "patch")
        self.assertIsNone(action_for(local, {"SKILL.md": sha}))
        self.assertEqual(action_for({}, {"SKILL.md": sha}), "remove")

    def test_command_uploads_to_target_and_isolates_batch_results(self):
        ctx = Context(self.root.parent)
        seen = []

        def fake_upload(*args, **kwargs):
            seen.append((args, kwargs))
            if args[2].endswith("report"):
                return {"skill": args[2], "status": "created"}
            raise RuntimeError("unexpected")

        with patch("ugh_cloud.command.upload_skill", side_effect=fake_upload):
            result = json.loads(handle_ugh("skill upload report --to-agent eve", ctx=ctx))
        self.assertEqual(result["agent"], "eve")
        self.assertEqual(result["results"][0]["skill"], "productivity/report")
        self.assertEqual(seen[0][0][1], "eve")

    def test_command_excludes_without_force(self):
        ctx = Context(self.root.parent, {"github-repo": "iwindd/ugh", "agent-name": "Lyla", "exclude": ["productivity/*"]})
        with patch("ugh_cloud.command.upload_skill") as upload:
            result = json.loads(handle_ugh("skill upload report", ctx=ctx))
        upload.assert_not_called()
        self.assertEqual(result["results"][0]["status"], "excluded")


if __name__ == "__main__":
    unittest.main()
