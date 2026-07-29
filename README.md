# CPT - Competitive Programming Tools

A CLI tool for stress-testing competitive programming solutions by comparing two programs on generated test data.

## Usage

```
python3 main.py compare <datagen> <program_a> <program_b> [options]
```

## Quick Start

Compile the examples and run a comparison:

```bash
g++ examples/aplusb/datagen.cpp -o datagen
g++ examples/aplusb/ac.cpp -o ac
g++ examples/aplusb/wa.cpp -o wa
python3 main.py compare ./datagen ./ac ./wa
```

## Options

| Option | Description |
|---|---|
| `datagen` | Path to the data generator executable |
| `program_a` | Path to program A (reference solution) |
| `program_b` | Path to program B (solution to test) |
| `-s, --strategy` | `nonstop` (default) or `limited_steps` |
| `-m, --mismatch` | Action on mismatch: `stop` (default), `continue`, or `pause` |
| `-n, --num-steps` | Number of test cases (default: 10, only for `limited_steps`) |
| `-j, --judger` | Path to judger script (default: `judgers/default.py`) |
| `-t, --max-runtime` | Max runtime in seconds per program (default: `1.0`). Use a tuple `(datagen, progA, progB, judger)` for per-program limits. Set negative for no limit. |

## How It Works

1. The **data generator** produces random test input.
2. **Program A** (reference) and **Program B** (candidate) each run on that input.
3. The **judger** compares their outputs and reports AC (accepted) or WA (wrong answer).
4. Depending on the strategy (`nonstop` or `limited_steps`), this repeats until a mismatch is found or the step limit is reached.

## Strategies

- **`nonstop`** — Runs indefinitely until a mismatch or `Ctrl+C`.
- **`limited_steps`** — Runs a fixed number of test cases (`-n`).

## Mismatch Handling

- **`stop`** (default) — Exit immediately on first mismatch.
- **`continue`** — Keep going after a mismatch.
- **`pause`** — Ask the user whether to continue.

## Built-in Judgers

| Judger | Description |
|---|---|
| `default` | Line-by-line exact comparison (trailing whitespace trimmed) |
| `noip` | Same as default (NOIP-style) |
| `caseinsensitive` | Case-insensitive line-by-line comparison |
| `charbychar` | Strict character-by-character comparison |
| `floatabserror` | Token-wise comparison with absolute error tolerance (1e-5) |
| `floatrelerror` | Token-wise comparison with relative error tolerance (1e-5) |
| `pertoken` | Token-by-token exact comparison |

## Custom Judgers

A judger is an executable file that reads three CLI arguments (data file, program A output, program B output) and outputs the validation result. Testlib judgers are directly compatible.

## Project Structure

```
├── main.py                  # CLI entry point
├── lib/
│   ├── common/__init__.py   # Subprocess and runtime utilities
│   └── compare.py           # Core comparison workflow
├── judgers/
│   ├── default.py           # Default line-by-line judger
│   ├── lib/__init__.py      # Base Validator class and helpers
│   └── ...                  # Other built-in judgers
└── examples/
    ├── aplusb/              # A+B problem (AC, WA, TLE, datagen)
    └── helloworld/          # Hello world (AC, WA variants, datagen)
```
