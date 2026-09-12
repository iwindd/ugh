import json
import shlex
import os
from pathlib import Path

from .github import upload_skill, UploadError


def _skill_root(ctx):
    home = getattr(ctx, "hermes_home", None) or os.environ.get("HERMES_HOME")
    return Path(home) / "skills" if home else Path.home() / ".hermes" / "skills"


def _agent_name(ctx):
    configured = ctx.get_config("agent-name", default="")
    return configured.strip() or str(getattr(ctx, "profile_name", "default"))


def _repo(ctx):
    return str(ctx.get_config("github-repo", default="")).strip()


def _exclude(ctx):
    value = ctx.get_config("exclude", default=[])
    return value if isinstance(value, list) else []


def _find_skill(root, skill_id):
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


def _all_skills(root):
    return [(p.parent.relative_to(root).as_posix(), p.parent) for p in sorted(root.rglob("SKILL.md"))]


def _excluded(skill_id, patterns):
    from fnmatch import fnmatch
    return any(fnmatch(skill_id, pattern) or fnmatch(skill_id.split("/", 1)[-1], pattern) for pattern in patterns)


def handle_ugh(raw_args, **kwargs):
    """Handle /ugh skill upload <skill-id>|all [--to-agent NAME] [--force]."""
    ctx = kwargs.get("ctx")
    if ctx is None:
        return json.dumps({"error": "plugin context unavailable"})
    try:
        args = shlex.split(raw_args or "")
        if len(args) < 3 or args[0:2] != ["skill", "upload"]:
            raise ValueError("usage: /ugh skill upload <skill-id>|all [--to-agent NAME] [--force]")
        selector = args[2]
        force = "--force" in args[3:]
        remove = "--remove" in args[3:]
        target = None
        i = 3
        while i < len(args):
            arg = args[i]
            if arg == "--to-agent":
                if i + 1 >= len(args) or args[i + 1].startswith("--"):
                    raise ValueError("--to-agent requires an agent name")
                target = args[i + 1]
                i += 2
                continue
            if arg.startswith("--to-agent="):
                target = arg.split("=", 1)[1]
                if not target:
                    raise ValueError("--to-agent requires an agent name")
            elif arg not in ("--force", "--remove"):
                raise ValueError(f"unknown option: {arg}")
            i += 1
        if not _repo(ctx):
            raise ValueError("configure github-repo in the ugh-cloud plugin settings")
        target = target or _agent_name(ctx)
        root = _skill_root(ctx)
        if remove and selector == "all":
            raise ValueError("--remove requires one qualified category/skill ID")
        if selector == "all":
            selected = _all_skills(root)
        else:
            try:
                selected = [_find_skill(root, selector)]
            except ValueError as exc:
                if not remove:
                    raise
                if "/" not in selector:
                    raise ValueError("--remove requires a qualified category/skill ID") from exc
                selected = [(selector, None)]
        results = []
        for skill_id, path in selected:
            if _excluded(skill_id, _exclude(ctx)) and not force:
                results.append({"skill": skill_id, "status": "excluded", "message": "use --force to confirm"})
                continue
            try:
                results.append(upload_skill(
                    _repo(ctx), target, skill_id, path, force=force,
                    source_profile=str(getattr(ctx, "profile_name", "active")),
                    command=raw_args,
                    remove=remove,
                ))
            except UploadError as exc:
                results.append({"skill": skill_id, "status": "failed", "error": str(exc)})
        return json.dumps({"success": True, "agent": target, "results": results})
    except (ValueError, UploadError) as exc:
        return json.dumps({"error": str(exc)})


def register(ctx):
    ctx.register_command(
        "ugh",
        handler=lambda raw: handle_ugh(raw, ctx=ctx),
        description="Upload profile skills to ugh-cloud GitHub pull requests",
    )
