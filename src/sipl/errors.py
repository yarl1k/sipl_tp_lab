"""Public error types for lexing, parsing, and program execution."""

from __future__ import annotations

from sipl.source import SourceSpan


class SIPLError(Exception):
    """Base class for errors that should be reported to a SIPL user."""

    def __init__(self, message: str, span: SourceSpan | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.span = span

    def to_dict(self) -> dict[str, object]:
        return {
            "type": type(self).__name__,
            "message": self.message,
            "span": self.span.to_dict() if self.span else None,
        }

    def __str__(self) -> str:
        if self.span is None:
            return self.message
        return (
            f"{self.message} "
            f"(рядок {self.span.start_line}, стовпець {self.span.start_column})"
        )


class LexError(SIPLError):
    """Raised when the source contains an unsupported character or token."""


class ParseError(SIPLError):
    """Raised when the token sequence does not match the SIPL grammar."""


class RuntimeSIPLError(SIPLError):
    """Raised when a well-formed program cannot be evaluated."""


class UndefinedVariableError(RuntimeSIPLError):
    """Raised when an expression reads a variable absent from the state."""


class StepLimitExceeded(RuntimeSIPLError):
    """Raised when execution exceeds the configured statement-step limit."""
