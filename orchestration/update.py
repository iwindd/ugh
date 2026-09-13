"""Pure update-check use case and installed-version discovery."""

import re
from pathlib import Path


class UpdateCheckError(RuntimeError):
    """An actionable, safe-to-display update-check error."""


_VERSION = re.compile(r"^[vV]?(\d+)\.(\d+)\.(\d+)$")


def _parse_version(value):
    match = _VERSION.fullmatch(str(value).strip())
    if not match:
        raise UpdateCheckError("release version is not a compatible semantic version")
    return tuple(int(part) for part in match.groups())


def installed_version(plugin_file=None):
    path = plugin_file or Path(__file__).resolve().parents[1] / "plugin.yaml"
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            value = line.split(":", 1)[1].strip().strip('"\'')
            _parse_version(value)
            return value
    raise UpdateCheckError("installed plugin version is unavailable")


def check_for_update(current, releases, update_command="hermes plugins update ugh"):
    """Compare *current* with the newest valid stable release from *releases*."""
    current_version = _parse_version(current)
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
            continue
        tag = release.get("tag_name")
        try:
            parsed = _parse_version(tag)
        except UpdateCheckError:
            continue
        candidates.append((parsed, str(tag).lstrip("vV"), release.get("html_url", "")))
    if not candidates:
        raise UpdateCheckError("no compatible stable GitHub release was found")
    latest, available, url = max(candidates)
    status = "update_available" if latest > current_version else "current"
    return {
        "status": status,
        "installed_version": str(current).lstrip("vV"),
        "available_version": available,
        "release_url": url,
        "update_command": update_command,
        "message": (
            f"ugh {available} is available. Review the release and run {update_command}."
            if status == "update_available"
            else f"ugh is up to date ({str(current).lstrip('vV')})."
        ),
    }