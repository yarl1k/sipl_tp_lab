"""Dependency-free SVG exporters for parse trees and ASTs."""

from sipl.visualization.ast_tree import ast_to_visual_node
from sipl.visualization.common import render_svg
from sipl.visualization.dot import _parse_visual
from sipl.visualization.parse_tree import ParseNode


def parse_tree_to_svg(root: ParseNode) -> str:
    return render_svg(_parse_visual(root), "SIPL Parse Tree")


def ast_to_svg(program) -> str:
    return render_svg(ast_to_visual_node(program), "SIPL AST")
