import importlib.util
import json
import pathlib
import tempfile
import sys

plugin = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ugh_cloud", plugin / "__init__.py", submodule_search_locations=[str(plugin)]
)
module = importlib.util.module_from_spec(spec)
sys.modules["ugh_cloud"] = module
spec.loader.exec_module(module)

from ugh_cloud.command import handle_ugh
from ugh_cloud.domain.planning import action_for, git_blob_sha

root = pathlib.Path(tempfile.mkdtemp())
skill = root / "skills" / "demo" / "sample"
skill.mkdir(parents=True)
(skill / "SKILL.md").write_text("---\nname: sample\n---\nhello\n", encoding="utf-8")

class Context:
    hermes_home = str(root)
    profile_name = "lyla"

    def get_config(self, key, default=None):
        return {"github-repo": "owner/repo", "agent-name": "Lyla", "exclude": []}.get(key, default)

seen = []
assert action_for({"SKILL.md": b"hello"}, {"SKILL.md": "".join([])}) == "patch"
sha = git_blob_sha(b"hello")
assert action_for({"SKILL.md": b"hello"}, {"SKILL.md": sha}) is None
import ugh_cloud.command as command
command.upload_skill = lambda *args, **kwargs: seen.append((args, kwargs)) or {"skill": args[2], "status": "created"}
result = json.loads(handle_ugh("skill upload sample --to-agent eve", ctx=Context()))
assert result["agent"] == "eve"
assert result["results"][0]["status"] == "created"
assert seen[0][0][2] == "demo/sample"
print("command test passed", result)
