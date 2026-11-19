"""Recursive-descent parser for the unambiguous SIPL grammar in docs/language-spec.md."""

from __future__ import annotations

from dataclasses import dataclass

from sipl import ast
from sipl.errors import ParseError
from sipl.lexer import tokenize
from sipl.source import SourceSpan, Token
from sipl.visualization.parse_tree import ParseNode, build_parse_tree


@dataclass(frozen=True, slots=True)
class ParseResult:
    ast: ast.Program
    parse_tree: ParseNode
    tokens: tuple[Token, ...]


class Parser:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens = tokenize(source)
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self.current
        if token.kind != "EOF":
            self.index += 1
        return token

    def _accept(self, kind: str) -> Token | None:
        if self.current.kind == kind:
            return self._advance()
        return None

    def _expect(self, kind: str, description: str | None = None) -> Token:
        if self.current.kind != kind:
            expected = description or kind.lower()
            actual = self.current.value or "кінець файлу"
            raise ParseError(
                f"Очікувався {expected}, отримано {actual!r}", self.current.span
            )
        return self._advance()

    @staticmethod
    def _combine(start: SourceSpan, end: SourceSpan) -> SourceSpan:
        return SourceSpan(
            start.start_offset,
            end.end_offset,
            start.start_line,
            start.start_column,
            end.end_line,
            end.end_column,
        )

    def parse(self) -> ast.Program:
        return self.parse_result().ast

    def parse_result(self) -> ParseResult:
        program = self._parse_program()
        self._expect("EOF", "кінець програми")
        tree = build_parse_tree(program, self.tokens)
        return ParseResult(program, tree, tuple(self.tokens))

    def _parse_program(self) -> ast.Program:
        begin = self._expect("BEGIN", "begin")
        body = self._parse_statement()
        end = self._expect("END", "end")
        return ast.Program(body, self._combine(begin.span, end.span))

    # Statement precedence, from strongest to weakest:
    # assignment / block / skip, while, if, sequence.
    def _parse_statement(self) -> ast.Statement:
        left = self._parse_if()
        while self._accept("SEMICOLON") is not None:
            right = self._parse_if()
            left = ast.Sequence(left, right, self._combine(left.span, right.span))
        return left

    def _parse_if(self) -> ast.Statement:
        if self.current.kind != "IF":
            return self._parse_while()
        start = self._advance()
        condition = self._parse_condition()
        self._expect("THEN", "then")
        then_branch = self._parse_while()
        self._expect("ELSE", "else")
        else_branch = self._parse_while()
        return ast.If(
            condition,
            then_branch,
            else_branch,
            self._combine(start.span, else_branch.span),
        )

    def _parse_while(self) -> ast.Statement:
        if self.current.kind != "WHILE":
            return self._parse_simple_statement()
        start = self._advance()
        condition = self._parse_condition()
        self._expect("DO", "do")
        body = self._parse_while()
        return ast.While(condition, body, self._combine(start.span, body.span))

    def _parse_simple_statement(self) -> ast.Statement:
        if (begin := self._accept("BEGIN")) is not None:
            statement = self._parse_statement()
            end = self._expect("END", "end")
            return ast.Block(statement, self._combine(begin.span, end.span))
        if (skip := self._accept("SKIP")) is not None:
            return ast.Skip(skip.span)
        variable = self._expect("VARIABLE", "змінна")
        self._expect("ASSIGN", ":=")
        expression = self._parse_arithmetic()
        return ast.Assign(
            variable.value,
            expression,
            self._combine(variable.span, expression.span),
        )

    # Boolean precedence: arithmetic comparisons, then NOT, then OR.
    def _parse_condition(self) -> ast.Condition:
        return self._parse_boolean_or()

    def _parse_boolean_or(self) -> ast.Condition:
        left = self._parse_boolean_not()
        while self.current.kind == "OR":
            self._advance()
            right = self._parse_boolean_not()
            left = ast.BoolOr(left, right, self._combine(left.span, right.span))
        return left

    def _parse_boolean_not(self) -> ast.Condition:
        if self.current.kind == "NOT":
            operator = self._advance()
            condition = self._parse_boolean_not()
            return ast.BoolNot(condition, self._combine(operator.span, condition.span))

        if self.current.kind == "LPAREN" and self._looks_like_boolean_group():
            opening = self._advance()
            condition = self._parse_condition()
            closing = self._expect("RPAREN", ")")
            return ast.ConditionGroup(condition, self._combine(opening.span, closing.span))

        left = self._parse_arithmetic()
        if self.current.kind not in {"EQUAL", "GREATER"}:
            raise ParseError(
                "Умова має містити порівняння (= або >), диз'юнкцію чи заперечення",
                self.current.span,
            )
        operator = self._advance()
        right = self._parse_arithmetic()
        return ast.Comparison(
            operator.value,
            left,
            right,
            self._combine(left.span, right.span),
        )

    def _looks_like_boolean_group(self) -> bool:
        """Distinguish (Bexp) from (Aexp) used as a comparison operand."""
        depth = 0
        cursor = self.index
        has_boolean_operator = False
        while cursor < len(self.tokens):
            kind = self.tokens[cursor].kind
            if kind == "LPAREN":
                depth += 1
            elif kind == "RPAREN":
                depth -= 1
                if depth == 0:
                    return has_boolean_operator
            elif kind in {"EQUAL", "GREATER", "OR", "NOT"}:
                has_boolean_operator = True
            elif kind == "EOF":
                return False
            cursor += 1
        return False

    # Arithmetic precedence: multiplication, then addition/subtraction.
    def _parse_arithmetic(self) -> ast.ArithmeticExpression:
        left = self._parse_term()
        while self.current.kind in {"PLUS", "MINUS"}:
            operator = self._advance()
            right = self._parse_term()
            left = ast.ArithmeticBinary(
                operator.value,
                left,
                right,
                self._combine(left.span, right.span),
            )
        return left

    def _parse_term(self) -> ast.ArithmeticExpression:
        left = self._parse_primary()
        while self.current.kind == "STAR":
            operator = self._advance()
            right = self._parse_primary()
            left = ast.ArithmeticBinary(
                operator.value,
                left,
                right,
                self._combine(left.span, right.span),
            )
        return left

    def _parse_primary(self) -> ast.ArithmeticExpression:
        if self.current.kind == "INTEGER":
            token = self._advance()
            return ast.Number(int(token.value), token.span)

        if (
            self.current.kind == "MINUS"
            and self.tokens[self.index + 1].kind == "INTEGER"
            and self.current.span.end_offset == self.tokens[self.index + 1].span.start_offset
        ):
            minus = self._advance()
            number = self._advance()
            return ast.Number(
                -int(number.value), self._combine(minus.span, number.span)
            )

        if self.current.kind == "VARIABLE":
            token = self._advance()
            return ast.Variable(token.value, token.span)

        if (opening := self._accept("LPAREN")) is not None:
            expression = self._parse_arithmetic()
            closing = self._expect("RPAREN", ")")
            return ast.ArithmeticGroup(
                expression, self._combine(opening.span, closing.span)
            )

        actual = self.current.value or "кінець файлу"
        raise ParseError(
            f"Очікувалося число, змінна або арифметичний вираз у дужках, отримано {actual!r}",
            self.current.span,
        )


def parse(source: str) -> ast.Program:
    """Parse SIPL source and return its typed AST."""

    return Parser(source).parse()


def parse_with_tree(source: str) -> ParseResult:
    """Parse SIPL source and return the AST together with its concrete parse tree."""

    return Parser(source).parse_result()
