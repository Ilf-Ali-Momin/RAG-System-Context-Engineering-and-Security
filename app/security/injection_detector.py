from __future__ import annotations

import re


INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all|previous|prior)\s+instructions?", re.IGNORECASE),
    re.compile(r"reveal\s+(system|hidden)\s+prompt", re.IGNORECASE),
    re.compile(r"developer\s+message", re.IGNORECASE),
    re.compile(r"jailbreak|do anything now|dan", re.IGNORECASE),
    re.compile(r"exfiltrate|leak|print\s+secrets?", re.IGNORECASE),
]


def detect_prompt_injection(text: str) -> list[str]:
    flags: list[str] = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            flags.append(pattern.pattern)
    return flags

