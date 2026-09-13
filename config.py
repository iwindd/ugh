"""Plugin configuration boundary."""

import os
from pathlib import Path


def skill_root(ctx):
    home = getattr(ctx, "hermes_home", None) or os.environ.get("HERMES_HOME")
    return Path(home) / "skills" if home else Path.home() / ".hermes" / "skills"


def agent_name(ctx):
    configured = ctx.get_config("agent-name", default="")
    return configured.strip() or str(getattr(ctx, "profile_name", "default"))


def repository(ctx):
    return str(ctx.get_config("github-repo", default="")).strip()


def exclusions(ctx):
    value = ctx.get_config("exclude", default=[])
    return value if isinstance(value, list) else []
