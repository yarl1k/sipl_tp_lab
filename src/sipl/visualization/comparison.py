"""Combined Parse Tree ↔ AST visualisation."""

from sipl import ast
from sipl.visualization.ast_tree import ast_to_visual_node
from sipl.visualization.common import VisualNode, render_dot, render_svg
from sipl.visualization.parse_tree import ParseNode, parse_tree_to_visual_node


def comparison_to_visual_node(parse_tree: ParseNode, program: ast.Program) -> VisualNode:
    return VisualNode(
        "SIPL: Parse Tree ↔ AST",
        (
            VisualNode("Parse Tree", (parse_tree_to_visual_node(parse_tree),)),
            VisualNode("AST", (ast_to_visual_node(program),)),
        ),
    )


def comparison_to_svg(parse_tree: ParseNode, program: ast.Program) -> str:
    return render_svg(comparison_to_visual_node(parse_tree, program), "SIPL Parse Tree vs AST")


def comparison_to_dot(parse_tree: ParseNode, program: ast.Program) -> str:
    return render_dot(comparison_to_visual_node(parse_tree, program), "SIPLComparison")
