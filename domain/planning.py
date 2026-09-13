"""Pure synchronization planning rules."""

import hashlib


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()


def action_for(local: dict[str, bytes], remote: dict[str, str]) -> str | None:
    local_sha = {name: git_blob_sha(content) for name, content in local.items()}
    if not remote:
        return "add" if local else None
    if not local:
        return "remove"
    return "patch" if local_sha != remote else None
