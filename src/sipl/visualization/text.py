"""Text rendering for parse trees and ASTs."""

from __future__ import annotations

from sipl import ast
from sipl.visualization.ast_tree import ast_to_visual_node
from sipl.visualization.common import VisualNode, render_text_tree
from sipl.visualization.parse_tree import ParseNode, TerminalNode


def parse_tree_to_text(root: ParseNode) -> str:
    def convert(node: ParseNode | TerminalNode) -> VisualNode:
        if isinstance(node, TerminalNode):
            return VisualNode(repr(node.value) if node.value else "EOF")
        return VisualNode(node.name, tuple(convert(child) for child in node.children))

    return render_text_tree(convert(root))


def ast_to_text(program: ast.Program) -> str:
    return render_text_tree(ast_to_visual_node(program))
