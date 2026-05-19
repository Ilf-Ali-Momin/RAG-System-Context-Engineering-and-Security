from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SessionTurn:
    user_query: str
    assistant_answer: str
    verified: bool


@dataclass
class SessionState:
    turns: list[SessionTurn] = field(default_factory=list)

    def add_turn(self, turn: SessionTurn, max_turns: int = 8) -> None:
        self.turns.append(turn)
        if len(self.turns) > max_turns:
            self.turns = self.turns[-max_turns:]

    def compact_verified_memory(self) -> str:
        verified_turns = [t for t in self.turns if t.verified]
        return "\n".join(
            f"Q: {turn.user_query}\nA: {turn.assistant_answer}"
            for turn in verified_turns[-3:]
        )


class MemoryStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState()
        return self._sessions[session_id]

