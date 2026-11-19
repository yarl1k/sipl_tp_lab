"""Runtime state for SIPL programs (a finite representation of Var -> Int)."""

from __future__ import annotations

from dataclasses import dataclass, field

from sipl.errors import UndefinedVariableError
from sipl.source import SourceSpan


@dataclass(slots=True)
class State:
    values: dict[str, int] = field(default_factory=dict)

    def read(self, name: str, span: SourceSpan | None = None) -> int:
        try:
            return self.values[name]
        except KeyError as exc:
            raise UndefinedVariableError(
                f"Змінна {name} не має значення у поточному стані", span
            ) from exc

    def assign(self, name: str, value: int) -> tuple[int | None, int]:
        old_value = self.values.get(name)
        self.values[name] = value
        return old_value, value

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self.values.items()))

    def copy(self) -> State:
        return State(self.snapshot())
