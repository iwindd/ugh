"""Hermes command parsing and result formatting boundary."""

import json
import shlex

from .config import agent_name, exclusions, repository, skill_root
from .github import UploadError
from .orchestration import upload_skill
from .skills.discovery import all_skills, find_skill
from .skills.safety import excluded


def handle_ugh(raw_args, **kwargs):
    """Handle /ugh skill upload <skill-id>|all [options]."""
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
        repo = repository(ctx)
        if not repo:
            raise ValueError("configure github-repo in the ugh-cloud plugin settings")
        target = target or agent_name(ctx)
        root = skill_root(ctx)
        if remove and selector == "all":
            raise ValueError("--remove requires one qualified category/skill ID")
        if selector == "all":
            selected = all_skills(root)
        else:
            try:
                selected = [find_skill(root, selector)]
            except ValueError as exc:
                if not remove or "/" not in selector:
                    raise
                selected = [(selector, None)]
        results = []
        for skill_id, path in selected:
            if excluded(skill_id, exclusions(ctx)) and not force:
                results.append({"skill": skill_id, "status": "excluded", "message": "use --force to confirm"})
                continue
            try:
                results.append(upload_skill(
                    repo, target, skill_id, path, force=force,
                    source_profile=str(getattr(ctx, "profile_name", "active")),
                    command=raw_args, remove=remove,
                ))
            except UploadError as exc:
                results.append({"skill": skill_id, "status": "failed", "error": str(exc)})
        return json.dumps({"success": True, "agent": target, "results": results})
    except (ValueError, UploadError) as exc:
        return json.dumps({"error": str(exc)})
