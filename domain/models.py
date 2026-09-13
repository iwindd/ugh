"""Pure data models for skill synchronization."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SkillRef:
    category: str
    skill_id: str


@dataclass(frozen=True)
class SkillSnapshot:
    files: Mapping[str, bytes]
    checksums: Mapping[str, str]


@dataclass(frozen=True)
class SyncPlan:
    action: str | None
    target: str


@dataclass(frozen=True)
class PullRequestRef:
    number: int | None
    state: str
    merged: bool
    branch: str
    url: str | None = None
