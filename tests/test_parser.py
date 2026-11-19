import unittest

from sipl import ast
from sipl.errors import ParseError
from sipl.parser import parse, parse_with_tree
from sipl.serialization import ast_shape
from sipl.visualization.parse_tree import ParseNode, TerminalNode


class ParserTests(unittest.TestCase):
    def test_parses_course_power_program(self):
        source = "begin R := 1; while Y > 0 do begin R := R * X; Y := Y - 1 end end"
        program = parse(source)
        self.assertIsInstance(program, ast.Program)
        self.assertTrue(ast_shape(program).startswith("Program("))

    def test_arithmetic_precedence_and_left_associativity(self):
        program = parse("begin X := A - B - C + D * E end")
        expression = program.body.expression
        self.assertIsInstance(expression, ast.ArithmeticBinary)
        self.assertEqual(expression.operator, "+")
        self.assertIsInstance(expression.left, ast.ArithmeticBinary)
        self.assertEqual(expression.left.operator, "-")
        self.assertIsInstance(expression.left.left, ast.ArithmeticBinary)
        self.assertEqual(expression.left.left.operator, "-")
        self.assertEqual(expression.right.operator, "*")

    def test_boolean_precedence(self):
        program = parse("begin if ¬ X = 1 ∨ Y > 2 then skip else skip end")
        conditional = program.body
        self.assertIsInstance(conditional, ast.If)
        self.assertIsInstance(conditional.condition, ast.BoolOr)
        self.assertIsInstance(conditional.condition.left, ast.BoolNot)

    def test_parentheses_distinguish_arithmetic_and_boolean_groups(self):
        program = parse("begin if (X + 1) > (Y * 2) ∨ (X = 0) then skip else skip end")
        condition = program.body.condition
        self.assertIsInstance(condition, ast.BoolOr)
        self.assertIsInstance(condition.left, ast.Comparison)
        self.assertIsInstance(condition.left.left, ast.ArithmeticGroup)
        self.assertIsInstance(condition.right, ast.ConditionGroup)

    def test_parse_tree_contains_all_terminal_tokens_in_order(self):
        source = "begin X := (1 + 2) * 3 end"
        result = parse_with_tree(source)
        self.assertIsInstance(result.parse_tree, ParseNode)
        leaves = []

        def visit(node):
            if isinstance(node, TerminalNode):
                leaves.append(node.value)
            else:
                for child in node.children:
                    visit(child)

        visit(result.parse_tree)
        self.assertEqual(" ".join(leaves), "begin X := ( 1 + 2 ) * 3 end")

    def test_negative_zero_keeps_its_parse_tree_sign(self):
        result = parse_with_tree("begin X := -0 end")
        leaves = []

        def visit(node):
            if isinstance(node, TerminalNode):
                leaves.append(node.value)
            else:
                for child in node.children:
                    visit(child)

        visit(result.parse_tree)
        self.assertEqual(" ".join(leaves), "begin X := - 0 end")

    def test_spaced_minus_is_not_a_signed_integer_literal(self):
        with self.assertRaises(ParseError):
            parse("begin X := - 1 end")

    def test_sequence_inside_control_branch_requires_block(self):
        with self.assertRaises(ParseError):
            parse("begin if X > 0 then X := 1; Y := 2 else skip end")

    def test_source_spans_are_present(self):
        program = parse("begin\n X := 10\nend")
        self.assertEqual(program.span.start_line, 1)
        self.assertEqual(program.body.span.start_line, 2)
        self.assertEqual(program.body.span.start_column, 2)

    def test_rejects_bad_programs(self):
        sources = (
            "X := 1 end", "begin X := 1", "begin X 1 end", "begin X := end",
            "begin if X > 0 then skip end", "begin end", "begin X := (1 + 2 end",
        )
        for source in sources:
            with self.subTest(source=source), self.assertRaises(ParseError):
                parse(source)


if __name__ == "__main__":
    unittest.main()
