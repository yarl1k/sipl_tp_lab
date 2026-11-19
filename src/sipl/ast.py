"""Typed abstract-syntax-tree nodes for the SIPL language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from sipl.source import SourceSpan


@dataclass(frozen=True, slots=True)
class Number:
    value: int
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Variable:
    name: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ArithmeticBinary:
    operator: str
    left: ArithmeticExpression
    right: ArithmeticExpression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ArithmeticGroup:
    expression: ArithmeticExpression
    span: SourceSpan


ArithmeticExpression: TypeAlias = Number | Variable | ArithmeticBinary | ArithmeticGroup


@dataclass(frozen=True, slots=True)
class Comparison:
    operator: str
    left: ArithmeticExpression
    right: ArithmeticExpression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class BoolOr:
    left: Condition
    right: Condition
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class BoolNot:
    condition: Condition
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ConditionGroup:
    condition: Condition
    span: SourceSpan


Condition: TypeAlias = Comparison | BoolOr | BoolNot | ConditionGroup


@dataclass(frozen=True, slots=True)
class Assign:
    variable: str
    expression: ArithmeticExpression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Sequence:
    first: Statement
    second: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class If:
    condition: Condition
    then_branch: Statement
    else_branch: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class While:
    condition: Condition
    body: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Block:
    statement: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Skip:
    span: SourceSpan


Statement: TypeAlias = Assign | Sequence | If | While | Block | Skip


@dataclass(frozen=True, slots=True)
class Program:
    body: Statement
    span: SourceSpan
