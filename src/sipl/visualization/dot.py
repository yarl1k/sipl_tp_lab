"""Graphviz DOT exporters."""

from sipl.visualization.ast_tree import ast_to_visual_node
from sipl.visualization.common import render_dot
from sipl.visualization.parse_tree import ParseNode, TerminalNode


def _parse_visual(node: ParseNode | TerminalNode):
    from sipl.visualization.common import VisualNode

    if isinstance(node, TerminalNode):
        return VisualNode(node.value if node.value else "EOF")
    return VisualNode(node.name, tuple(_parse_visual(child) for child in node.children))


def parse_tree_to_dot(root: ParseNode) -> str:
    return render_dot(_parse_visual(root), "SIPLParseTree")


def ast_to_dot(program) -> str:
    return render_dot(ast_to_visual_node(program), "SIPL_AST")
