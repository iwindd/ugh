import importlib.util
import json
import pathlib
import tempfile
import sys

plugin = pathlib.Path(r"C:/Users/kongt/AppData/Local/hermes/profiles/lyla/plugins/ugh-cloud")
spec = importlib.util.spec_from_file_location(
    "ugh_cloud", plugin / "__init__.py", submodule_search_locations=[str(plugin)]
)
module = importlib.util.module_from_spec(spec)
sys.modules["ugh_cloud"] = module
spec.loader.exec_module(module)

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
assert module.github._action({"SKILL.md": b"hello"}, {"SKILL.md": "".join([])}) == "patch"
sha = __import__("hashlib").sha1(b"blob 5\0hello").hexdigest()
assert module.github._action({"SKILL.md": b"hello"}, {"SKILL.md": sha}) is None
module.upload_skill = lambda *args, **kwargs: seen.append((args, kwargs)) or {"skill": args[2], "status": "created"}
result = json.loads(module.handle_ugh("skill upload sample --to-agent eve", ctx=Context()))
assert result["agent"] == "eve"
assert result["results"][0]["status"] == "created"
assert seen[0][0][2] == "demo/sample"
print("command test passed", result)
