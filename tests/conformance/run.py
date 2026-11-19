"""Run the portable conformance fixtures against the installed sipl package."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sipl.errors import SIPLError
from sipl.interpreter import execute
from sipl.parser import parse_with_tree
from sipl.serialization import ast_shape


HERE = Path(__file__).resolve().parent


def main() -> int:
    manifest = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    passed = 0
    failed = 0

    for case in manifest["valid"]:
        source = (HERE / "valid" / case["file"]).read_text(encoding="utf-8")
        try:
            parsed = parse_with_tree(source)
            actual_shape = ast_shape(parsed.ast)
            if actual_shape != case["expected_ast"]:
                raise AssertionError(f"AST mismatch: {actual_shape}")
            result = execute(parsed.ast, case["initial_state"])
            if result.final_state != case["expected_state"]:
                raise AssertionError(f"State mismatch: {result.final_state}")
            passed += 1
            print(f"PASS valid/{case['file']}")
        except Exception as error:  # Report each fixture and continue to the next one.
            failed += 1
            print(f"FAIL valid/{case['file']}: {error}", file=sys.stderr)

    for case in manifest["invalid"]:
        source = (HERE / "invalid" / case["file"]).read_text(encoding="utf-8")
        try:
            parse_with_tree(source)
        except SIPLError as error:
            if type(error).__name__ != case["expected_error"]:
                failed += 1
                print(
                    f"FAIL invalid/{case['file']}: expected {case['expected_error']}, "
                    f"got {type(error).__name__}",
                    file=sys.stderr,
                )
            else:
                passed += 1
                print(f"PASS invalid/{case['file']}")
        except Exception as error:
            failed += 1
            print(f"FAIL invalid/{case['file']}: unexpected {error}", file=sys.stderr)
        else:
            failed += 1
            print(f"FAIL invalid/{case['file']}: invalid source was accepted", file=sys.stderr)

    print(f"\nConformance: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
