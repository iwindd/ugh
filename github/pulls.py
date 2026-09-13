import shutil
import subprocess

from .client import UploadError


class PullRequests:
    """GitHub pull-request lookup and creation."""

    def __init__(self, client): self.client = client
    def list(self, state): return self.client.request("GET", "/pulls", query={"state": state, "per_page": 100})

    def find(self, branch):
        for state in ("open", "closed"):
            for pull in self.list(state):
                if pull.get("head", {}).get("ref") == branch: return pull
        return None

    def create(self, title, body, branch, base):
        payload = {"title": title, "body": body, "head": branch, "base": base}
        try:
            return self.client.request("POST", "/pulls", payload)
        except UploadError as exc:
            if "403" not in str(exc) or "Resource not accessible" not in str(exc) or not shutil.which("gh"): raise
            try:
                fallback = subprocess.check_output(["gh", "auth", "token"], text=True, timeout=10).strip()
            except (OSError, subprocess.SubprocessError) as token_exc:
                raise exc from token_exc
            if not fallback: raise
            previous = self.client.token
            try:
                self.client.token = fallback
                return self.client.request("POST", "/pulls", payload)
            finally:
                self.client.token = previous
