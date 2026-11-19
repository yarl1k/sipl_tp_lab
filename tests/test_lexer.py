import unittest

from sipl.errors import LexError
from sipl.lexer import tokenize


class LexerTests(unittest.TestCase):
    def test_tokenizes_keywords_variables_and_operators(self):
        tokens = tokenize("begin X := -12; if X > 0 ∨ ¬ (Y = 1) then skip else end")
        self.assertEqual(
            [token.kind for token in tokens],
            ["BEGIN", "VARIABLE", "ASSIGN", "MINUS", "INTEGER", "SEMICOLON", "IF",
             "VARIABLE", "GREATER", "INTEGER", "OR", "NOT", "LPAREN", "VARIABLE",
             "EQUAL", "INTEGER", "RPAREN", "THEN", "SKIP", "ELSE", "END", "EOF"],
        )

    def test_tracks_line_and_column(self):
        tokens = tokenize("begin\n  X := 2\nend")
        variable = next(token for token in tokens if token.kind == "VARIABLE")
        self.assertEqual((variable.span.start_line, variable.span.start_column), (2, 3))

    def test_rejects_unknown_character(self):
        with self.assertRaises(LexError):
            tokenize("begin X := 1 @ end")
        with self.assertRaises(LexError):
            tokenize("begin X := ١ end")

    def test_rejects_lowercase_and_multi_letter_names(self):
        with self.assertRaises(LexError):
            tokenize("begin x := 1 end")
        with self.assertRaises(LexError):
            tokenize("begin AB := 1 end")


if __name__ == "__main__":
    unittest.main()
