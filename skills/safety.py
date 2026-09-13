"""Skill exclusion and safety policy."""

import re
from fnmatch import fnmatch


def excluded(skill_id, patterns):
    return any(fnmatch(skill_id, pattern) or fnmatch(skill_id.split("/", 1)[-1], pattern) for pattern in patterns)


def suspicious_files(files):
    patterns = (".env", ".pem", ".key", ".p12", ".pfx", "credentials", "token", "secret")
    key_re = re.compile(rb"-----BEGIN .*PRIVATE KEY-----|(?:api[_-]?key|access[_-]?token|secret)\\s*[:=]\\s*[^\\s]+", re.I)
    return sorted({name for name, content in files.items() if any(part in name.lower() for part in patterns) or key_re.search(content)})
