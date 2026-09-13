import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


class UploadError(RuntimeError):
    """An actionable error raised while synchronizing a skill."""


class GitHub:
    """Authenticated GitHub REST transport with compatibility delegates."""

    def __init__(self, repo):
        if not re.fullmatch(r"[^/\\s]+/[^/\\s]+", repo):
            raise UploadError("github-repo must be in owner/repository form")
        self.repo = repo
        self.base = f"https://api.github.com/repos/{repo}"
        self.token = os.getenv("UGH_CLOUD_GITHUB_TOKEN", "").strip()
        if not self.token:
            raise UploadError("UGH_CLOUD_GITHUB_TOKEN is not configured")
        from .bootstrap import Bootstrap
        from .git_data import GitData
        from .pulls import PullRequests
        self.git_data = GitData(self)
        self.pull_requests = PullRequests(self)
        self.bootstrap = Bootstrap(self)

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

    # Compatibility delegates retain the established GitHub public interface.
    def ref(self, branch): return self.git_data.ref(branch)
    def ref_exists(self, branch): return self.git_data.ref_exists(branch)
    def commit(self, sha): return self.git_data.commit(sha)
    def tree(self, sha): return self.git_data.tree(sha)
    def blob(self, content): return self.git_data.blob(content)
    def create_ref(self, branch, sha): return self.git_data.create_ref(branch, sha)
    def update_ref(self, branch, sha): return self.git_data.update_ref(branch, sha)
    def create_tree(self, base_tree, entries): return self.git_data.create_tree(base_tree, entries)
    def create_commit(self, message, tree, parent): return self.git_data.create_commit(message, tree, parent)
    def initialize_branch(self, branch): return self.bootstrap.initialize_branch(branch)
    def pulls(self, state): return self.pull_requests.list(state)
    def find_pull(self, branch): return self.pull_requests.find(branch)
    def create_pull(self, title, body, branch, base): return self.pull_requests.create(title, body, branch, base)


def upload_skill(*args, **kwargs):
    """Compatibility import for the established upload entry point."""
    from .upload import upload_skill as implementation
    return implementation(*args, **kwargs)

__all__ = ["GitHub", "UploadError", "upload_skill"]
