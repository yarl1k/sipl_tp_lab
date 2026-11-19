import unittest

from sipl.errors import StepLimitExceeded, UndefinedVariableError
from sipl.interpreter import Interpreter, State, execute
from sipl.parser import parse


class InterpreterTests(unittest.TestCase):
    def test_power_program_and_final_state(self):
        source = "begin R := 1; while Y > 0 do begin R := R * X; Y := Y - 1 end end"
        result = execute(parse(source), {"X": 5, "Y": 2})
        self.assertEqual(result.final_state, {"R": 25, "X": 5, "Y": 0})
        self.assertGreater(result.steps, 0)

    def test_all_statement_forms_and_arithmetic(self):
        source = "begin A := 8; B := 3; C := (A - B) * 2; if C = 10 then begin D := C + 1 end else D := 0 end"
        result = execute(parse(source))
        self.assertEqual(result.final_state, {"A": 8, "B": 3, "C": 10, "D": 11})

    def test_boolean_or_and_not(self):
        source = "begin if X > 0 ∨ ¬ (Y = 0) then Z := 1 else Z := 0 end"
        result = execute(parse(source), {"X": 0, "Y": 2})
        self.assertEqual(result.final_state["Z"], 1)

    def test_or_evaluates_both_predicates(self):
        source = "begin if X > 0 ∨ Y > 0 then Z := 1 else Z := 0 end"
        with self.assertRaises(UndefinedVariableError):
            execute(parse(source), {"X": 1})

    def test_undefined_variable_is_reported(self):
        with self.assertRaises(UndefinedVariableError):
            execute(parse("begin X := Y + 1 end"))

    def test_step_limit_stops_non_terminating_loop(self):
        program = parse("begin while X = 0 do skip end")
        with self.assertRaises(StepLimitExceeded):
            execute(program, {"X": 0}, max_steps=5)

    def test_trace_contains_required_events_and_sequence_numbers(self):
        result = execute(parse("begin X := 2; if X > 1 then skip else X := 0 end"))
        types = [event.type for event in result.trace.events]
        self.assertIn("BeforeStatement", types)
        self.assertIn("AfterStatement", types)
        self.assertIn("VariableChanged", types)
        self.assertIn("ConditionChecked", types)
        self.assertEqual([event.sequence for event in result.trace.events], list(range(1, len(types) + 1)))
        self.assertEqual(types[0], "ProgramStarted")
        self.assertEqual(types[-1], "ProgramFinished")

    def test_trace_reports_failed_execution(self):
        interpreter = Interpreter()
        with self.assertRaises(UndefinedVariableError):
            interpreter.run(parse("begin X := Y end"))
        self.assertEqual(interpreter.trace.events[-1].type, "ProgramFailed")

    def test_state_helpers(self):
        state = State({"X": 1})
        self.assertEqual(state.read("X"), 1)
        self.assertEqual(state.assign("X", 2), (1, 2))
        self.assertEqual(state.snapshot(), {"X": 2})
        self.assertEqual(state.copy().snapshot(), {"X": 2})

    def test_interpreter_can_be_reused(self):
        interpreter = Interpreter()
        first = interpreter.run(parse("begin X := 1 end"))
        second = interpreter.run(parse("begin Y := 2 end"))
        self.assertEqual(first.steps, second.steps)
        self.assertEqual(second.final_state, {"Y": 2})


if __name__ == "__main__":
    unittest.main()
