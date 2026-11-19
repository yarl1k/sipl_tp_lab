import unittest

from sipl.parser import parse, parse_with_tree
from sipl.visualization import (
    ast_to_dot,
    ast_to_svg,
    ast_to_text,
    comparison_to_svg,
    parse_tree_to_dot,
    parse_tree_to_svg,
    parse_tree_to_text,
)


class VisualizationTests(unittest.TestCase):
    def setUp(self):
        self.result = parse_with_tree("begin X := 1 + 2 end")

    def test_parse_tree_text_contains_concrete_tokens(self):
        output = parse_tree_to_text(self.result.parse_tree)
        self.assertIn("Assignment", output)
        self.assertIn("':='", output)
        self.assertIn("'begin'", output)

    def test_ast_text_is_abstract(self):
        output = ast_to_text(self.result.ast)
        self.assertIn("Assign X", output)
        self.assertIn("Arithmetic +", output)

    def test_comparison_svg_contains_both_representations(self):
        output = comparison_to_svg(self.result.parse_tree, self.result.ast)
        self.assertIn("Parse Tree", output)
        self.assertIn("AST", output)


    def test_ast_renderer_handles_control_flow_and_blocks(self):
        source = (
            "begin X := 2; while X > 0 do begin "
            "if ¬ (X = 1) then skip else begin X := X - 1 end; "
            "X := X - 1 end end"
        )
        output = ast_to_text(parse(source))
        for label in ("Sequence", "While", "Block", "If", "Skip", "NOT ¬", "Compare ="):
            self.assertIn(label, output)

    def test_svg_and_dot_exports(self):
        parse_svg = parse_tree_to_svg(self.result.parse_tree)
        ast_svg = ast_to_svg(self.result.ast)
        self.assertTrue(parse_svg.startswith("<svg"))
        self.assertTrue(ast_svg.startswith("<svg"))
        self.assertIn("digraph", parse_tree_to_dot(self.result.parse_tree))
        self.assertIn("digraph", ast_to_dot(self.result.ast))


if __name__ == "__main__":
    unittest.main()
