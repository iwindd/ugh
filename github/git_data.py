import base64
import urllib.parse

from .client import UploadError


class GitData:
    """GitHub Git Data operations for refs, objects, trees, and commits."""

    def __init__(self, client): self.client = client

    def ref(self, branch):
        return self.client.request("GET", f"/git/ref/heads/{urllib.parse.quote(branch, safe='')}")

    def ref_exists(self, branch):
        try:
            self.ref(branch)
            return True
        except UploadError as exc:
            return "GitHub API 404" not in str(exc)

    def commit(self, sha): return self.client.request("GET", f"/git/commits/{sha}")
    def tree(self, sha): return self.client.request("GET", f"/git/trees/{sha}", query={"recursive": "1"}).get("tree", [])

    def blob(self, content):
        return self.client.request("POST", "/git/blobs", {"content": base64.b64encode(content).decode(), "encoding": "base64"})["sha"]

    def create_ref(self, branch, sha):
        return self.client.request("POST", "/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})

    def update_ref(self, branch, sha):
        return self.client.request("PATCH", f"/git/refs/heads/{urllib.parse.quote(branch, safe='')}", {"sha": sha, "force": False})

    def create_tree(self, base_tree, entries):
        payload = {"tree": entries}
        if base_tree: payload["base_tree"] = base_tree
        return self.client.request("POST", "/git/trees", payload)["sha"]

    def create_commit(self, message, tree, parent):
        payload = {"message": message, "tree": tree}
        if parent: payload["parents"] = [parent]
        return self.client.request("POST", "/git/commits", payload)["sha"]

    def remote_files(self, commit_sha, prefix):
        tree = self.tree(self.commit(commit_sha)["tree"]["sha"])
        marker = prefix.rstrip("/") + "/"
        return {item["path"][len(marker):]: item["sha"] for item in tree if item.get("type") == "blob" and item["path"].startswith(marker)}
