"""SIPL Language Toolkit public package."""

__version__ = "0.1.0"

from sipl.parser import ParseResult, Parser, parse, parse_with_tree

__all__ = ["ParseResult", "Parser", "__version__", "parse", "parse_with_tree"]
