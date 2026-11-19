"""Small dependency-free tree rendering helpers (text, Graphviz DOT, and SVG)."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape


@dataclass(frozen=True, slots=True)
class VisualNode:
    label: str
    children: tuple[VisualNode, ...] = field(default_factory=tuple)


def render_text_tree(root: VisualNode) -> str:
    lines = [root.label]

    def visit(node: VisualNode, prefix: str) -> None:
        for index, child in enumerate(node.children):
            last = index == len(node.children) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.label)
            visit(child, prefix + ("    " if last else "│   "))

    visit(root, "")
    return "\n".join(lines)


def render_dot(root: VisualNode, graph_name: str = "SIPLTree") -> str:
    lines = [f'digraph {graph_name} {{', '  node [shape=box, style="rounded", fontname="Arial"];']
    counter = 0

    def visit(node: VisualNode) -> int:
        nonlocal counter
        node_id = counter
        counter += 1
        label = node.label.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        lines.append(f'  n{node_id} [label="{label}"];')
        for child in node.children:
            child_id = visit(child)
            lines.append(f"  n{node_id} -> n{child_id};")
        return node_id

    visit(root)
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_svg(root: VisualNode, title: str = "SIPL tree") -> str:
    """Render a readable top-down SVG without requiring Graphviz or a browser framework."""
    leaf_counter = 0
    positions: dict[int, tuple[float, float]] = {}
    depths: dict[int, int] = {}
    nodes: dict[int, VisualNode] = {}
    parents: list[tuple[int, int]] = []
    next_id = 0

    def layout(node: VisualNode, depth: int) -> tuple[int, float]:
        nonlocal leaf_counter, next_id
        node_id = next_id
        next_id += 1
        nodes[node_id] = node
        depths[node_id] = depth
        child_positions: list[tuple[int, float]] = []
        for child in node.children:
            child_positions.append(layout(child, depth + 1))
            parents.append((node_id, child_positions[-1][0]))
        if not child_positions:
            x = 90.0 + leaf_counter * 170.0
            leaf_counter += 1
        else:
            x = sum(position for _, position in child_positions) / len(child_positions)
        positions[node_id] = (x, 65.0 + depth * 105.0)
        return node_id, x

    root_id, _ = layout(root, 0)
    leaf_count = max(1, leaf_counter)
    width = max(600.0, 180.0 * leaf_count)
    max_depth = max(depths.values(), default=0)
    height = 115.0 + (max_depth + 1) * 105.0

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{escape(title)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="20" y="25" font-family="Arial, sans-serif" font-size="16" fill="#333">{escape(title)}</text>',
    ]

    for parent_id, child_id in parents:
        px, py = positions[parent_id]
        cx, cy = positions[child_id]
        pieces.append(
            f'<path d="M {px:.1f} {py + 20:.1f} V {((py + cy) / 2):.1f} H {cx:.1f} V {cy - 20:.1f}" '
            'fill="none" stroke="#64748b" stroke-width="1.5"/>'
        )

    for node_id, node in nodes.items():
        x, y = positions[node_id]
        box_width = max(100.0, min(230.0, len(node.label) * 7.2 + 26.0))
        box_height = 38.0
        pieces.append(
            f'<rect x="{x - box_width / 2:.1f}" y="{y - box_height / 2:.1f}" '
            f'width="{box_width:.1f}" height="{box_height:.1f}" rx="7" '
            'fill="#f8fafc" stroke="#475569" stroke-width="1.2"/>'
        )
        pieces.append(
            f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="12" fill="#0f172a">{escape(node.label)}</text>'
        )

    pieces.append("</svg>")
    return "\n".join(pieces)
