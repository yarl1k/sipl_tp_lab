"""Concrete parse-tree representation and AST-to-parse-tree projection."""

from __future__ import annotations

from dataclasses import dataclass

from sipl import ast
from sipl.source import SourceSpan, Token


@dataclass(frozen=True, slots=True)
class TerminalNode:
    kind: str
    value: str
    span: SourceSpan

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "terminal",
            "kind": self.kind,
            "value": self.value,
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ParseNode:
    name: str
    children: tuple[ParseNode | TerminalNode, ...]
    span: SourceSpan

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "nonterminal",
            "name": self.name,
            "children": [child.to_dict() for child in self.children],
            "span": self.span.to_dict(),
        }


def build_parse_tree(program: ast.Program, tokens: list[Token]) -> ParseNode:
    """Build a concrete, source-linked tree while retaining all grammar tokens."""

    def terminal(kind: str, start: int, end: int) -> TerminalNode:
        for token in tokens:
            if (
                token.kind == kind
                and token.span.start_offset >= start
                and token.span.end_offset <= end
            ):
                return TerminalNode(token.kind, token.value, token.span)
        raise ValueError(f"Не вдалося знайти токен {kind} у діапазоні {start}:{end}")

    def between(kind: str, left: SourceSpan, right: SourceSpan) -> TerminalNode:
        return terminal(kind, left.end_offset, right.start_offset)

    def visit_expr(node: ast.ArithmeticExpression) -> ParseNode:
        if isinstance(node, ast.Number):
            children: list[ParseNode | TerminalNode] = []
            if any(
                token.kind == "MINUS" and token.span.start_offset == node.span.start_offset
                for token in tokens
            ):
                children.append(terminal("MINUS", node.span.start_offset, node.span.end_offset))
            children.append(terminal("INTEGER", node.span.start_offset, node.span.end_offset))
            return ParseNode("Number", tuple(children), node.span)
        if isinstance(node, ast.Variable):
            return ParseNode(
                "Variable", (terminal("VARIABLE", node.span.start_offset, node.span.end_offset),), node.span
            )
        if isinstance(node, ast.ArithmeticGroup):
            return ParseNode(
                "ArithmeticGroup",
                (
                    terminal("LPAREN", node.span.start_offset, node.expression.span.start_offset),
                    visit_expr(node.expression),
                    terminal("RPAREN", node.expression.span.end_offset, node.span.end_offset),
                ),
                node.span,
            )
        if isinstance(node, ast.ArithmeticBinary):
            return ParseNode(
                "ArithmeticExpression",
                (
                    visit_expr(node.left),
                    between("PLUS" if node.operator == "+" else "MINUS" if node.operator == "-" else "STAR", node.left.span, node.right.span),
                    visit_expr(node.right),
                ),
                node.span,
            )
        raise TypeError(f"Невідомий вузол арифметичного виразу: {type(node).__name__}")

    def visit_condition(node: ast.Condition) -> ParseNode:
        if isinstance(node, ast.Comparison):
            kind = "EQUAL" if node.operator == "=" else "GREATER"
            return ParseNode(
                "Comparison",
                (visit_expr(node.left), between(kind, node.left.span, node.right.span), visit_expr(node.right)),
                node.span,
            )
        if isinstance(node, ast.BoolOr):
            return ParseNode(
                "BooleanExpression",
                (visit_condition(node.left), between("OR", node.left.span, node.right.span), visit_condition(node.right)),
                node.span,
            )
        if isinstance(node, ast.BoolNot):
            return ParseNode(
                "Negation",
                (
                    terminal("NOT", node.span.start_offset, node.condition.span.start_offset),
                    visit_condition(node.condition),
                ),
                node.span,
            )
        if isinstance(node, ast.ConditionGroup):
            return ParseNode(
                "ConditionGroup",
                (
                    terminal("LPAREN", node.span.start_offset, node.condition.span.start_offset),
                    visit_condition(node.condition),
                    terminal("RPAREN", node.condition.span.end_offset, node.span.end_offset),
                ),
                node.span,
            )
        raise TypeError(f"Невідомий вузол умови: {type(node).__name__}")

    def visit_statement(node: ast.Statement) -> ParseNode:
        if isinstance(node, ast.Assign):
            variable_token = terminal("VARIABLE", node.span.start_offset, node.expression.span.start_offset)
            assign_token = terminal("ASSIGN", variable_token.span.end_offset, node.expression.span.start_offset)
            return ParseNode(
                "Assignment",
                (variable_token, assign_token, visit_expr(node.expression)),
                node.span,
            )
        if isinstance(node, ast.Sequence):
            return ParseNode(
                "Sequence",
                (
                    visit_statement(node.first),
                    between("SEMICOLON", node.first.span, node.second.span),
                    visit_statement(node.second),
                ),
                node.span,
            )
        if isinstance(node, ast.If):
            return ParseNode(
                "IfStatement",
                (
                    terminal("IF", node.span.start_offset, node.condition.span.start_offset),
                    visit_condition(node.condition),
                    terminal("THEN", node.condition.span.end_offset, node.then_branch.span.start_offset),
                    visit_statement(node.then_branch),
                    terminal("ELSE", node.then_branch.span.end_offset, node.else_branch.span.start_offset),
                    visit_statement(node.else_branch),
                ),
                node.span,
            )
        if isinstance(node, ast.While):
            return ParseNode(
                "WhileStatement",
                (
                    terminal("WHILE", node.span.start_offset, node.condition.span.start_offset),
                    visit_condition(node.condition),
                    terminal("DO", node.condition.span.end_offset, node.body.span.start_offset),
                    visit_statement(node.body),
                ),
                node.span,
            )
        if isinstance(node, ast.Block):
            return ParseNode(
                "Block",
                (
                    terminal("BEGIN", node.span.start_offset, node.statement.span.start_offset),
                    visit_statement(node.statement),
                    terminal("END", node.statement.span.end_offset, node.span.end_offset),
                ),
                node.span,
            )
        if isinstance(node, ast.Skip):
            return ParseNode(
                "Skip", (terminal("SKIP", node.span.start_offset, node.span.end_offset),), node.span
            )
        raise TypeError(f"Невідомий оператор: {type(node).__name__}")

    return ParseNode(
        "Program",
        (
            terminal("BEGIN", program.span.start_offset, program.body.span.start_offset),
            visit_statement(program.body),
            terminal("END", program.body.span.end_offset, program.span.end_offset),
        ),
        program.span,
    )


def parse_tree_to_visual_node(root: ParseNode):
    """Convert a Parse Tree to the shared renderer's neutral tree model."""
    from sipl.visualization.common import VisualNode

    def visit(node: ParseNode | TerminalNode) -> VisualNode:
        if isinstance(node, TerminalNode):
            return VisualNode(node.value if node.value else "EOF")
        return VisualNode(node.name, tuple(visit(child) for child in node.children))

    return visit(root)
