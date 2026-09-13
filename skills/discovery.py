"""Category-aware skill discovery."""

from pathlib import Path


def find_skill(root: Path, skill_id: str):
    requested = Path(skill_id)
    if requested.is_absolute() or ".." in requested.parts:
        raise ValueError("skill-id must be a category/skill or skill name")
    if len(requested.parts) > 1:
        candidate = root.joinpath(*requested.parts)
        if (candidate / "SKILL.md").is_file():
            return "/".join(requested.parts), candidate
        raise ValueError(f"skill not found: {skill_id}")
    matches = sorted(p.parent for p in root.glob(f"*/{requested.name}/SKILL.md"))
    if not matches:
        raise ValueError(f"skill not found: {skill_id}")
    if len(matches) > 1:
        choices = ", ".join(p.relative_to(root).as_posix() for p in matches)
        raise ValueError(f"multiple skills found for {skill_id}: {choices}; use category/{skill_id}")
    return matches[0].relative_to(root).as_posix(), matches[0]


def all_skills(root: Path):
    return [(p.parent.relative_to(root).as_posix(), p.parent) for p in sorted(root.rglob("SKILL.md"))]
