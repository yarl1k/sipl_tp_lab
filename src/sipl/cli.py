"""Command-line interface for parsing, checking, running, and tracing SIPL."""

from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from sipl.errors import SIPLError
from sipl.interpreter import Interpreter
from sipl.parser import parse_with_tree
from sipl.serialization import ast_to_dict, parse_tree_to_dict
from sipl.visualization import (
    ast_to_dot,
    comparison_to_dot,
    comparison_to_svg,
    ast_to_svg,
    ast_to_text,
    parse_tree_to_dot,
    parse_tree_to_svg,
    parse_tree_to_text,
)

try:
    __version__ = version("sipl-language-toolkit")
except PackageNotFoundError:
    __version__ = "0.1.0"

def _add_source_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("file", type=Path, help="шлях до файлу .sipl")


def _add_format_argument(
    parser: argparse.ArgumentParser, choices: tuple[str, ...], default: str = "text"
) -> None:
    parser.add_argument("--format", choices=choices, default=default, help="формат результату")


def _add_execution_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--set",
        dest="initial_values",
        action="append",
        default=[],
        metavar="X=VALUE",
        help="початкове значення змінної; параметр можна повторювати",
    )
    parser.add_argument(
        "--max-steps", type=int, default=100_000, help="максимальна кількість виконаних операторів"
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sipl",
        description="SIPL Language Toolkit: parser, interpreter, trace та візуалізація дерев.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse", help="побудувати Parse Tree та AST")
    _add_source_argument(parse_parser)
    _add_format_argument(parse_parser, ("text", "json", "dot", "svg"))
    parse_parser.add_argument(
        "--view", choices=("parse-tree", "ast", "both"), default="both",
        help="яке дерево виводити; both — порівняння Parse Tree та AST",
    )
    parse_parser.add_argument("--output", type=Path, help="записати результат у файл")

    check_parser = subparsers.add_parser("check", help="перевірити синтаксичну коректність")
    _add_source_argument(check_parser)
    _add_format_argument(check_parser, ("text", "json"))

    run_parser = subparsers.add_parser("run", help="виконати програму")
    _add_source_argument(run_parser)
    _add_format_argument(run_parser, ("text", "json"))
    _add_execution_arguments(run_parser)

    trace_parser = subparsers.add_parser("trace", help="виконати програму та вивести події Trace")
    _add_source_argument(trace_parser)
    _add_format_argument(trace_parser, ("text", "json"))
    _add_execution_arguments(trace_parser)

    return parser


def _load_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Не вдалося прочитати файл {path}: {exc}") from exc


def _parse_initial_state(values: list[str]) -> dict[str, int]:
    state: dict[str, int] = {}

    for item in values:
        if "=" not in item:
            raise ValueError(
                f"Некоректне початкове значення {item!r}; очікується X=VALUE"
            )

        name, raw_value = item.split("=", 1)

        if (
            len(name) != 1
            or not name.isascii()
            or not name.isupper()
            or not name.isalpha()
        ):
            raise ValueError(
                f"Некоректна назва змінної {name!r}; "
                "очікується одна велика літера"
            )

        if name in state:
            raise ValueError(
                f"Початкове значення змінної {name} задано повторно"
            )

        try:
            state[name] = int(raw_value)
        except ValueError as exc:
            raise ValueError(
                f"Значення змінної {name} має бути цілим числом"
            ) from exc

    return state


def _state_text(state: dict[str, int]) -> str:
    if not state:
        return "{}"
    return "{" + ", ".join(f"{name} → {value}" for name, value in state.items()) + "}"


def _format_parse_result(result, output_format: str, view: str) -> str:
    if output_format == "json":
        return json.dumps(
            {
                "schema_version": "1.0",
                "status": "ok",
                "parse_tree": parse_tree_to_dict(result.parse_tree),
                "ast": ast_to_dict(result.ast),
            },
            ensure_ascii=False,
            indent=2,
        )
    if output_format == "dot":
        if view == "ast":
            return ast_to_dot(result.ast)
        if view == "both":
            return comparison_to_dot(result.parse_tree, result.ast)
        return parse_tree_to_dot(result.parse_tree)
    if output_format == "svg":
        if view == "ast":
            return ast_to_svg(result.ast)
        if view == "both":
            return comparison_to_svg(result.parse_tree, result.ast)
        return parse_tree_to_svg(result.parse_tree)
    if view == "parse-tree":
        return parse_tree_to_text(result.parse_tree)
    if view == "ast":
        return ast_to_text(result.ast)
    return (
        "=== Parse Tree ===\n"
        + parse_tree_to_text(result.parse_tree)
        + "\n\n=== AST ===\n"
        + ast_to_text(result.ast)
    )


def _write_result(text: str, output: Path | None) -> None:
    if output is None:
        print(text)
    else:
        output.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
        print(f"Результат записано у {output}")


def _run_command(args: argparse.Namespace) -> int:
    source = _load_source(args.file)
    parsed = parse_with_tree(source)

    if args.command == "parse":
        result = _format_parse_result(parsed, args.format, args.view)
        _write_result(result, args.output)
        return 0

    if args.command == "check":
        payload = {"schema_version": "1.0", "status": "ok", "valid": True}
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"{args.file}: синтаксично коректна SIPL-програма")
        return 0

    initial_state = _parse_initial_state(args.initial_values)
    execution = Interpreter(max_steps=args.max_steps).run(parsed.ast, initial_state)

    if args.format == "json":
        payload = execution.to_dict(include_trace=args.command == "trace")
        payload["initial_state"] = dict(sorted(initial_state.items()))
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "run":
        print(f"Початковий стан: {_state_text(dict(sorted(initial_state.items())))}")
        print(f"Кінцевий стан:    {_state_text(execution.final_state)}")
        print(f"Кількість кроків: {execution.steps}")
        return 0

    for event in execution.trace.events:
        location = ""
        if event.span is not None:
            location = f" ({event.span.start_line}:{event.span.start_column})"
        details = f" {event.details}" if event.details else ""
        print(f"{event.sequence:03d} {event.type}{location}: {event.message}{details}")
    print(f"\nКінцевий стан: {_state_text(execution.final_state)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        return _run_command(args)
    except SIPLError as error:
        if getattr(args, "format", "text") == "json":
            print(
                json.dumps(
                    {"schema_version": "1.0", "status": "error", "error": error.to_dict()},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Помилка: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        if getattr(args, "format", "text") == "json":
            print(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "status": "error",
                        "error": {"type": type(error).__name__, "message": str(error), "span": None},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Помилка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
