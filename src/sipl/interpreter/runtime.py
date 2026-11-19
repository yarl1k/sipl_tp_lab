"""Interpreter implementing the compositional SIPL execution rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sipl import ast
from sipl.errors import RuntimeSIPLError, StepLimitExceeded
from sipl.interpreter.events import ExecutionEvent
from sipl.interpreter.state import State
from sipl.interpreter.trace import ExecutionTrace
from sipl.source import SourceSpan


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    final_state: dict[str, int]
    steps: int
    trace: ExecutionTrace

    def to_dict(self, include_trace: bool = False) -> dict[str, object]:
        result: dict[str, object] = {
            "schema_version": "1.0",
            "status": "ok",
            "final_state": self.final_state,
            "steps": self.steps,
        }
        if include_trace:
            result["events"] = self.trace.to_list()
        return result


class Interpreter:
    """Execute AST statements and emit Before/After/condition/state events."""

    def __init__(self, max_steps: int = 100_000) -> None:
        if max_steps < 1:
            raise ValueError("max_steps має бути додатним цілим числом")
        self.max_steps = max_steps
        self.state = State()
        self.steps = 0
        self.trace = ExecutionTrace()

    def run(
        self,
        program: ast.Program,
        initial_state: dict[str, int] | None = None,
    ) -> ExecutionResult:
        self.state = State(dict(initial_state or {}))
        self.steps = 0
        self.trace = ExecutionTrace()
        self._emit("ProgramStarted", "Початок виконання програми", program.span)
        try:
            self._execute(program.body)
        except RuntimeSIPLError as error:
            self._emit(
                "ProgramFailed",
                str(error),
                error.span,
                {"error_type": type(error).__name__},
            )
            raise
        self._emit("ProgramFinished", "Виконання програми завершено", program.span)
        return ExecutionResult(self.state.snapshot(), self.steps, self.trace)

    def _emit(
        self,
        event_type: str,
        message: str,
        span: SourceSpan | None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.trace.append(
            ExecutionEvent(
                sequence=len(self.trace.events) + 1,
                type=event_type,
                message=message,
                span=span,
                state=self.state.snapshot(),
                details=details or {},
            )
        )

    @staticmethod
    def _statement_name(statement: ast.Statement) -> str:
        names = {
            ast.Assign: "Assign",
            ast.Sequence: "Sequence",
            ast.If: "If",
            ast.While: "While",
            ast.Block: "Block",
            ast.Skip: "Skip",
        }
        return names[type(statement)]

    def _execute(self, statement: ast.Statement) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise StepLimitExceeded(
                f"Перевищено ліміт виконання ({self.max_steps} кроків)", statement.span
            )

        statement_name = self._statement_name(statement)
        self._emit(
            "BeforeStatement",
            f"Початок оператора {statement_name}",
            statement.span,
            {"statement": statement_name, "step": self.steps},
        )

        if isinstance(statement, ast.Assign):
            new_value = self._evaluate_arithmetic(statement.expression)
            old_value, _ = self.state.assign(statement.variable, new_value)
            self._emit(
                "VariableChanged",
                f"Змінна {statement.variable}: {old_value!r} -> {new_value}",
                statement.span,
                {
                    "variable": statement.variable,
                    "old_value": old_value,
                    "new_value": new_value,
                },
            )
        elif isinstance(statement, ast.Sequence):
            self._execute(statement.first)
            self._execute(statement.second)
        elif isinstance(statement, ast.If):
            condition_value = self._evaluate_condition(statement.condition)
            self._emit_condition(statement.condition, condition_value, "if", 0)
            self._execute(statement.then_branch if condition_value else statement.else_branch)
        elif isinstance(statement, ast.While):
            iteration = 0
            while True:
                condition_value = self._evaluate_condition(statement.condition)
                self._emit_condition(statement.condition, condition_value, "while", iteration)
                if not condition_value:
                    break
                iteration += 1
                self._execute(statement.body)
        elif isinstance(statement, ast.Block):
            self._execute(statement.statement)
        elif isinstance(statement, ast.Skip):
            pass
        else:
            raise TypeError(f"Невідомий тип оператора: {type(statement).__name__}")

        self._emit(
            "AfterStatement",
            f"Завершення оператора {statement_name}",
            statement.span,
            {"statement": statement_name, "step": self.steps},
        )

    def _emit_condition(
        self, condition: ast.Condition, value: bool, construct: str, iteration: int
    ) -> None:
        self._emit(
            "ConditionChecked",
            f"Умова {construct}: {'true' if value else 'false'}",
            condition.span,
            {"construct": construct, "result": value, "iteration": iteration},
        )

    def _evaluate_arithmetic(self, expression: ast.ArithmeticExpression) -> int:
        if isinstance(expression, ast.Number):
            return expression.value
        if isinstance(expression, ast.Variable):
            return self.state.read(expression.name, expression.span)
        if isinstance(expression, ast.ArithmeticGroup):
            return self._evaluate_arithmetic(expression.expression)
        if isinstance(expression, ast.ArithmeticBinary):
            left = self._evaluate_arithmetic(expression.left)
            right = self._evaluate_arithmetic(expression.right)
            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right
        raise TypeError(f"Невідомий тип арифметичного виразу: {type(expression).__name__}")

    def _evaluate_condition(self, condition: ast.Condition) -> bool:
        if isinstance(condition, ast.Comparison):
            left = self._evaluate_arithmetic(condition.left)
            right = self._evaluate_arithmetic(condition.right)
            if condition.operator == "=":
                return left == right
            if condition.operator == ">":
                return left > right
        if isinstance(condition, ast.BoolOr):
            # Superposition evaluates both predicates in the current state.
            left = self._evaluate_condition(condition.left)
            right = self._evaluate_condition(condition.right)
            return left or right
        if isinstance(condition, ast.BoolNot):
            return not self._evaluate_condition(condition.condition)
        if isinstance(condition, ast.ConditionGroup):
            return self._evaluate_condition(condition.condition)
        raise TypeError(f"Невідомий тип умови: {type(condition).__name__}")


def execute(
    program: ast.Program,
    initial_state: dict[str, int] | None = None,
    max_steps: int = 100_000,
) -> ExecutionResult:
    """Convenience function for one program execution."""

    return Interpreter(max_steps=max_steps).run(program, initial_state)
