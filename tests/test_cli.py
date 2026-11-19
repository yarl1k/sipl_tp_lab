import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from sipl.cli import main


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(list(args))
        return code, output.getvalue()

    def test_check_json(self):
        code, output = self.run_cli("check", "examples/power.sipl", "--format", "json")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output)["valid"])


    def test_parse_json_contains_parse_tree_and_ast(self):
        code, output = self.run_cli("parse", "examples/power.sipl", "--format", "json")
        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["ast"]["type"], "Program")
        self.assertEqual(payload["parse_tree"]["name"], "Program")
        self.assertIn("span", payload["ast"])

    def test_run_example(self):
        code, output = self.run_cli("run", "examples/power.sipl", "--set", "X=5", "--set", "Y=2")
        self.assertEqual(code, 0)
        self.assertIn("R → 25", output)

    def test_trace_json(self):
        code, output = self.run_cli(
            "trace", "examples/conditional.sipl", "--set", "X=2", "--format", "json"
        )
        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["status"], "ok")
        self.assertIn("events", payload)

    def test_parse_svg_to_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "tree.svg"
            code, output = self.run_cli(
                "parse", "examples/power.sipl", "--format", "svg", "--view", "ast",
                "--output", str(target),
            )
            self.assertEqual(code, 0)
            self.assertTrue(target.read_text(encoding="utf-8").startswith("<svg"))
            self.assertIn("записано", output)


    def test_parse_both_svg(self):
        code, output = self.run_cli(
            "parse", "examples/power.sipl", "--format", "svg", "--view", "both"
        )
        self.assertEqual(code, 0)
        self.assertIn("Parse Tree", output)
        self.assertIn("AST", output)

    def test_json_error(self):
        code, output = self.run_cli(
            "check", "tests/conformance/invalid/missing_end.sipl", "--format", "json"
        )
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["status"], "error")


if __name__ == "__main__":
    unittest.main()
