"""Project typed AST nodes into a compact visual tree."""

from __future__ import annotations

from sipl import ast
from sipl.visualization.common import VisualNode


def ast_to_visual_node(node: ast.Program | ast.Statement | ast.ArithmeticExpression | ast.Condition) -> VisualNode:
    if isinstance(node, ast.Program):
        return VisualNode("Program", (ast_to_visual_node(node.body),))
    if isinstance(node, ast.Assign):
        return VisualNode(f"Assign {node.variable}", (ast_to_visual_node(node.expression),))
    if isinstance(node, ast.Sequence):
        return VisualNode("Sequence", (ast_to_visual_node(node.first), ast_to_visual_node(node.second)))
    if isinstance(node, ast.If):
        return VisualNode(
            "If",
            (
                ast_to_visual_node(node.condition),
                ast_to_visual_node(node.then_branch),
                ast_to_visual_node(node.else_branch),
            ),
        )
    if isinstance(node, ast.While):
        return VisualNode("While", (ast_to_visual_node(node.condition), ast_to_visual_node(node.body)))
    if isinstance(node, ast.Block):
        return VisualNode("Block", (ast_to_visual_node(node.statement),))
    if isinstance(node, ast.Skip):
        return VisualNode("Skip")
    if isinstance(node, ast.Number):
        return VisualNode(f"Number {node.value}")
    if isinstance(node, ast.Variable):
        return VisualNode(f"Variable {node.name}")
    if isinstance(node, ast.ArithmeticBinary):
        return VisualNode(
            f"Arithmetic {node.operator}",
            (ast_to_visual_node(node.left), ast_to_visual_node(node.right)),
        )
    if isinstance(node, ast.ArithmeticGroup):
        return VisualNode("Arithmetic Group", (ast_to_visual_node(node.expression),))
    if isinstance(node, ast.Comparison):
        return VisualNode(
            f"Compare {node.operator}",
            (ast_to_visual_node(node.left), ast_to_visual_node(node.right)),
        )
    if isinstance(node, ast.BoolOr):
        return VisualNode("OR ∨", (ast_to_visual_node(node.left), ast_to_visual_node(node.right)))
    if isinstance(node, ast.BoolNot):
        return VisualNode("NOT ¬", (ast_to_visual_node(node.condition),))
    if isinstance(node, ast.ConditionGroup):
        return VisualNode("Condition Group", (ast_to_visual_node(node.condition),))
    raise TypeError(f"Невідомий тип AST-вузла: {type(node).__name__}")
