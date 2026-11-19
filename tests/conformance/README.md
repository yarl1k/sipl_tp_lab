# SIPL Conformance Suite

The conformance fixture format is intended to be implementation-neutral. An
implementation adapter reads `cases.json`, parses each `.sipl` source, compares
the compact AST shape and final state for valid cases, and checks the public
error category for invalid cases.

- `valid/`: positive programs.
- `invalid/`: negative programs.
- `cases.json`: expected AST shapes, input states, output states, and error kinds.
- `schema.json`: JSON Schema for the manifest format.
- `run.py`: adapter for this Python implementation.

The current suite contains 12 positive and 12 negative cases. Run it from the
repository root after installing the package:

```bash
python tests/conformance/run.py
```

The adapter is an example; another SIPL implementation can consume the same
fixtures with its own parser/runtime and compare against the same manifest.
