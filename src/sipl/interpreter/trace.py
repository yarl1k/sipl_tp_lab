"""Container for an ordered sequence of execution events."""

from __future__ import annotations

from dataclasses import dataclass, field

from sipl.interpreter.events import ExecutionEvent


@dataclass(slots=True)
class ExecutionTrace:
    events: list[ExecutionEvent] = field(default_factory=list)

    def append(self, event: ExecutionEvent) -> None:
        self.events.append(event)

    def to_list(self) -> list[dict[str, object]]:
        return [event.to_dict() for event in self.events]
