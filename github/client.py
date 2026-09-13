import base64
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from ..domain.planning import action_for
from ..skills.safety import suspicious_files
from ..skills.snapshot import files as snapshot_files


class UploadError(RuntimeError):
    pass


class GitHub:
    def __init__(self, repo):
        if not re.fullmatch(r"[^/\\s]+/[^/\\s]+", repo):
            raise UploadError("github-repo must be in owner/repository form")
        self.repo = repo
        self.base = f"https://api.github.com/repos/{repo}"
        self.token = os.getenv("UGH_CLOUD_GITHUB_TOKEN", "").strip()
        if not self.token:
            raise UploadError("UGH_CLOUD_GITHUB_TOKEN is not configured")

    def request(self, method, path, payload=None, query=None):
        url = self.base + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("Authorization", f"Bearer {self.token}")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode() or "{}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise UploadError(f"GitHub API {exc.code}: {detail[:500]}") from exc
        except urllib.error.URLError as exc:
            raise UploadError(f"GitHub connection failed: {exc.reason}") from exc

    def default_branch(self):
        return self.request("GET", "")["default_branch"]

    def ref(self, branch):
        return self.request("GET", f"/git/ref/heads/{urllib.parse.quote(branch, safe='')}")

    def ref_exists(self, branch):
        try:
            self.ref(branch)
            return True
        except UploadError as exc:
            return "GitHub API 404" not in str(exc)

    def commit(self, sha):
        return self.request("GET", f"/git/commits/{sha}")

    def tree(self, sha):
        return self.request("GET", f"/git/trees/{sha}", query={"recursive": "1"}).get("tree", [])

    def blob(self, content):
        return self.request("POST", "/git/blobs", {"content": base64.b64encode(content).decode(), "encoding": "base64"})["sha"]

    def create_ref(self, branch, sha):
        return self.request("POST", "/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})

    def update_ref(self, branch, sha):
        return self.request("PATCH", f"/git/refs/heads/{urllib.parse.quote(branch, safe='')}", {"sha": sha, "force": False})

    def create_tree(self, base_tree, entries):
        payload = {"tree": entries}
        if base_tree:
            payload["base_tree"] = base_tree
        return self.request("POST", "/git/trees", payload)["sha"]

    def create_commit(self, message, tree, parent):
        payload = {"message": message, "tree": tree}
        if parent:
            payload["parents"] = [parent]
        return self.request("POST", "/git/commits", payload)["sha"]

    def initialize_branch(self, branch):
        # GitHub rejects creating a tree in a repository with no commits.
        # The Contents API is the supported bootstrap path for empty repos.
        self.request(
            "PUT",
            "/contents/.gitkeep",
            {
                "message": "chore: initialize repository",
                "content": base64.b64encode(b"").decode(),
            },
        )
        return self.ref(branch)

    def pulls(self, state):
        return self.request("GET", "/pulls", query={"state": state, "per_page": 100})

    def find_pull(self, branch):
        for state in ("open", "closed"):
            for pull in self.pulls(state):
                if pull.get("head", {}).get("ref") == branch:
                    return pull
        return None

    def create_pull(self, title, body, branch, base):
        payload = {"title": title, "body": body, "head": branch, "base": base}
        try:
            return self.request("POST", "/pulls", payload)
        except UploadError as exc:
            # A user may have a valid gh login while the configured
            # fine-grained token lacks Pull requests: write.
            if "403" not in str(exc) or "Resource not accessible" not in str(exc) or not shutil.which("gh"):
                raise
            try:
                fallback = subprocess.check_output(["gh", "auth", "token"], text=True, timeout=10).strip()
            except (OSError, subprocess.SubprocessError) as token_exc:
                raise exc from token_exc
            if not fallback:
                raise
            previous = self.token
            try:
                self.token = fallback
                return self.request("POST", "/pulls", payload)
            finally:
                self.token = previous


def _remote_files(github, commit_sha, prefix):
    tree = github.tree(github.commit(commit_sha)["tree"]["sha"])
    marker = prefix.rstrip("/") + "/"
    return {item["path"][len(marker):]: item["sha"] for item in tree if item.get("type") == "blob" and item["path"].startswith(marker)}


def _safe_component(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip(".-")
    if not value:
        raise UploadError("agent name/category/skill ID cannot be empty")
    return value


def upload_skill(repo, agent_name, skill_id, skill_path, force=False, source_profile="active", command="", remove=False):
    parts = skill_id.split("/", 1)
    if len(parts) != 2:
        raise UploadError("skill ID must include category/skill")
    category, short_id = (_safe_component(x) for x in parts)
    agent = _safe_component(agent_name)
    try:
        local = {} if remove else snapshot_files(Path(skill_path))
    except RuntimeError as exc:
        raise UploadError(str(exc)) from exc
    suspicious = suspicious_files(local)
    if suspicious and not force:
        raise UploadError("possible secret files detected; use --force to confirm: " + ", ".join(suspicious))

    gh = GitHub(repo)
    base = gh.default_branch()
    branch = f"ugh-cloud/agents/{agent}/skills/{category}/{short_id}"
    target = f"agents/{agent}/skills/{category}/{short_id}"
    existing = gh.find_pull(branch)
    parent = None
    pr_url = None
    previous_url = None
    if existing and (existing.get("state") == "closed" or existing.get("merged_at") is not None):
        previous_url = existing.get("html_url")
        suffix = 2
        candidate = f"{branch}-{suffix}"
        while gh.ref_exists(candidate):
            suffix += 1
            candidate = f"{branch}-{suffix}"
        branch = candidate
        existing = None
    elif not existing and gh.ref_exists(branch):
        # A previous run may have created the branch but failed before PR creation.
        suffix = 2
        candidate = f"{branch}-{suffix}"
        while gh.ref_exists(candidate):
            suffix += 1
            candidate = f"{branch}-{suffix}"
        branch = candidate
    if existing:
        parent = existing["head"]["sha"]
        pr_url = existing.get("html_url")
        remote = _remote_files(gh, parent, target)
    else:
        try:
            base_ref = gh.ref(base)
        except UploadError as exc:
            if "Git Repository is empty" not in str(exc):
                raise
            base_ref = gh.initialize_branch(base)
        parent = base_ref["object"]["sha"]
        remote = _remote_files(gh, parent, target)
    action = action_for(local, remote)
    if action is None:
        return {"skill": skill_id, "action": "noop", "status": "success", "message": "remote content is identical", "pr_url": pr_url}

    entries = []
    all_names = sorted(set(local) | set(remote))
    for name in all_names:
        path = f"{target}/{name}"
        if name not in local:
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
        else:
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": gh.blob(local[name])})
    base_tree = gh.commit(parent)["tree"]["sha"]
    tree = gh.create_tree(base_tree, entries)
    message = f"chore({agent}): {action} skill {short_id}"
    commit = gh.create_commit(message, tree, parent)
    if not existing:
        gh.create_ref(branch, parent)
    gh.update_ref(branch, commit)
    display = agent_name.strip() or agent
    if display.islower():
        display = display.title()
    title = f"[{display}] Request to {action} skill `{short_id}`"
    body = "\n".join([
        f"Source profile: {source_profile}",
        f"Target agent: {display}",
        f"Skill: {skill_id}",
        f"Action: {action}",
        f"Command: /ugh {command}",
        "", "Files:", *[f"- {n}" for n in sorted(local)],
        "", "Generated by: ugh-cloud", f"Force upload: {'yes' if force else 'no'}",
    ])
    if suspicious:
        body += "\n\nForce warnings acknowledged for:\n" + "\n".join(f"- {n}" for n in suspicious)
    if previous_url:
        body += f"\n\nPrevious closed PR: {previous_url}"
    if pr_url:
        return {"skill": skill_id, "action": action, "status": "updated", "pr_url": pr_url, "branch": branch}
    pull = gh.create_pull(title, body, branch, base)
    return {"skill": skill_id, "action": action, "status": "created", "pr_url": pull.get("html_url"), "branch": branch}
