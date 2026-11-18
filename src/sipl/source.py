"""Source locations and lexical tokens used throughout the SIPL toolkit."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A half-open source range; line and column numbers are one-based."""

    start_offset: int
    end_offset: int
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    value: str
    span: SourceSpan

    def to_dict(self) -> dict[str, object]:
        return {"kind": self.kind, "value": self.value, "span": self.span.to_dict()}
