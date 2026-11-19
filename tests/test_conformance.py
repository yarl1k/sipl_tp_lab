import json
import unittest
from pathlib import Path

from sipl.errors import SIPLError
from sipl.interpreter import execute
from sipl.parser import parse_with_tree
from sipl.serialization import ast_shape


ROOT = Path(__file__).parent / "conformance"


class ConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))

    def test_valid_programs(self):
        for case in self.manifest["valid"]:
            with self.subTest(case=case["file"]):
                source = (ROOT / "valid" / case["file"]).read_text(encoding="utf-8")
                parsed = parse_with_tree(source)
                self.assertEqual(ast_shape(parsed.ast), case["expected_ast"])
                result = execute(parsed.ast, case["initial_state"])
                self.assertEqual(result.final_state, case["expected_state"])

    def test_invalid_programs(self):
        for case in self.manifest["invalid"]:
            with self.subTest(case=case["file"]):
                source = (ROOT / "invalid" / case["file"]).read_text(encoding="utf-8")
                with self.assertRaises(SIPLError) as context:
                    parse_with_tree(source)
                self.assertEqual(type(context.exception).__name__, case["expected_error"])


if __name__ == "__main__":
    unittest.main()
