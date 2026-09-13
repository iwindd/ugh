"""Complete skill-directory snapshots."""

from pathlib import Path


def files(root):
    if root is None:
        return {}
    result = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"symlinks are not allowed in skills: {path.name}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    if "SKILL.md" not in result:
        raise RuntimeError("skill directory must contain SKILL.md")
    return result
