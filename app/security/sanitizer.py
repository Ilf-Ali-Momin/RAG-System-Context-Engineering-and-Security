from __future__ import annotations

import re
import unicodedata


CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
SECRET_RE = re.compile(
    r"(sk-[a-zA-Z0-9]{16,}|api[_-]?key\s*[:=]\s*[\w-]{8,}|password\s*[:=]\s*\S+)",
    re.IGNORECASE,
)


def sanitize_text(text: str, max_chars: int) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = CONTROL_CHARS_RE.sub(" ", normalized)
    normalized = MULTI_SPACE_RE.sub(" ", normalized)
    return normalized.strip()[:max_chars]


def redact_secrets(text: str) -> str:
    return SECRET_RE.sub("[REDACTED]", text)

