"""A dependency-free lexer for the lexical elements used by SIPL."""

from __future__ import annotations

from collections.abc import Iterator

from sipl.errors import LexError
from sipl.source import SourceSpan, Token


KEYWORDS = {
    "begin": "BEGIN",
    "end": "END",
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "while": "WHILE",
    "do": "DO",
    "skip": "SKIP",
}

SINGLE_CHAR_TOKENS = {
    ";": "SEMICOLON",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "=": "EQUAL",
    ">": "GREATER",
    "(": "LPAREN",
    ")": "RPAREN",
    "∨": "OR",
    "¬": "NOT",
}


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1

    def _span(self, start: tuple[int, int, int]) -> SourceSpan:
        start_offset, start_line, start_column = start
        return SourceSpan(
            start_offset=start_offset,
            end_offset=self.index,
            start_line=start_line,
            start_column=start_column,
            end_line=self.line,
            end_column=self.column,
        )

    def _advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.index < len(self.source):
            char = self.source[self.index]
            if char.isspace():
                self._advance()
                continue

            start = (self.index, self.line, self.column)

            if char in "0123456789":
                begin = self.index
                while self.index < len(self.source) and self.source[self.index] in "0123456789":
                    self._advance()
                tokens.append(Token("INTEGER", self.source[begin:self.index], self._span(start)))
                continue

            if char.isascii() and char.isalpha():
                begin = self.index
                while (
                    self.index < len(self.source)
                    and self.source[self.index].isascii()
                    and self.source[self.index].isalpha()
                ):
                    self._advance()
                value = self.source[begin:self.index]
                if value in KEYWORDS:
                    kind = KEYWORDS[value]
                elif len(value) == 1 and value.isupper():
                    kind = "VARIABLE"
                elif value.isupper():
                    raise LexError(
                        "Назва змінної має складатися з однієї великої латинської літери",
                        self._span(start),
                    )
                else:
                    raise LexError(f"Невідоме ключове слово або ідентифікатор: {value!r}", self._span(start))
                tokens.append(Token(kind, value, self._span(start)))
                continue

            if self.source.startswith(":=", self.index):
                self._advance()
                self._advance()
                tokens.append(Token("ASSIGN", ":=", self._span(start)))
                continue

            if char in SINGLE_CHAR_TOKENS:
                self._advance()
                tokens.append(Token(SINGLE_CHAR_TOKENS[char], char, self._span(start)))
                continue

            raise LexError(f"Непідтримуваний символ: {char!r}", self._span(start))

        eof_span = SourceSpan(
            self.index, self.index, self.line, self.column, self.line, self.column
        )
        tokens.append(Token("EOF", "", eof_span))
        return tokens

    def __iter__(self) -> Iterator[Token]:
        return iter(self.tokenize())


def tokenize(source: str) -> list[Token]:
    """Tokenize source and append an explicit EOF token."""

    return Lexer(source).tokenize()
