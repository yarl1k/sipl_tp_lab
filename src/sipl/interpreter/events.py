"""Execution event model used by tracing and future debugger integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sipl.source import SourceSpan


@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    sequence: int
    type: str
    message: str
    span: SourceSpan | None
    state: dict[str, int]
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "type": self.type,
            "message": self.message,
            "span": self.span.to_dict() if self.span else None,
            "state": self.state,
            "details": self.details,
        }
