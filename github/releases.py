"""Unauthenticated GitHub Releases API adapter for update discovery."""

import json
import urllib.error
import urllib.request


class ReleaseCheckError(RuntimeError):
    """Raised when the public releases endpoint cannot be read."""


class Releases:
    """Read-only transport for a repository's GitHub releases."""

    def __init__(self, repo="iwindd/ugh"):
        self.repo = repo
        self.url = f"https://api.github.com/repos/{repo}/releases"

    def list(self):
        request = urllib.request.Request(self.url, method="GET")
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode() or "[]")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, TimeoutError, ValueError) as exc:
            raise ReleaseCheckError("unable to read public GitHub releases") from exc
        if not isinstance(payload, list):
            raise ReleaseCheckError("GitHub returned an invalid releases response")
        return payload