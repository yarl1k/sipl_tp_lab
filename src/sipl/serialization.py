"""Stable JSON representations for AST and parse-tree data."""

from __future__ import annotations

from dataclasses import fields
from typing import Any

from sipl import ast
from sipl.source import SourceSpan
from sipl.visualization.parse_tree import ParseNode, TerminalNode


def ast_to_dict(node: Any) -> object:
    if isinstance(node, SourceSpan):
        return node.to_dict()
    if isinstance(node, tuple):
        return [ast_to_dict(item) for item in node]
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    if hasattr(node, "__dataclass_fields__"):
        result: dict[str, object] = {"type": type(node).__name__}
        for item in fields(node):
            result[item.name] = ast_to_dict(getattr(node, item.name))
        return result
    return node


def parse_tree_to_dict(node: ParseNode | TerminalNode) -> dict[str, object]:
    return node.to_dict()


def ast_shape(node: Any) -> str:
    """Compact, deterministic AST shape used by the conformance manifest."""
    if isinstance(node, ast.Program):
        return f"Program({ast_shape(node.body)})"
    if isinstance(node, ast.Assign):
        return f"Assign({node.variable},{ast_shape(node.expression)})"
    if isinstance(node, ast.Sequence):
        return f"Sequence({ast_shape(node.first)},{ast_shape(node.second)})"
    if isinstance(node, ast.If):
        return f"If({ast_shape(node.condition)},{ast_shape(node.then_branch)},{ast_shape(node.else_branch)})"
    if isinstance(node, ast.While):
        return f"While({ast_shape(node.condition)},{ast_shape(node.body)})"
    if isinstance(node, ast.Block):
        return f"Block({ast_shape(node.statement)})"
    if isinstance(node, ast.Skip):
        return "Skip"
    if isinstance(node, ast.Number):
        return f"Number({node.value})"
    if isinstance(node, ast.Variable):
        return f"Variable({node.name})"
    if isinstance(node, ast.ArithmeticBinary):
        return f"Arithmetic{node.operator}({ast_shape(node.left)},{ast_shape(node.right)})"
    if isinstance(node, ast.ArithmeticGroup):
        return f"ArithmeticGroup({ast_shape(node.expression)})"
    if isinstance(node, ast.Comparison):
        return f"Compare{node.operator}({ast_shape(node.left)},{ast_shape(node.right)})"
    if isinstance(node, ast.BoolOr):
        return f"Or({ast_shape(node.left)},{ast_shape(node.right)})"
    if isinstance(node, ast.BoolNot):
        return f"Not({ast_shape(node.condition)})"
    if isinstance(node, ast.ConditionGroup):
        return f"ConditionGroup({ast_shape(node.condition)})"
    raise TypeError(f"Невідомий тип AST-вузла: {type(node).__name__}")
