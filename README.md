# CPT - Competitive Programming Tools

A CLI tool for stress-testing competitive programming solutions by comparing two programs on randomly generated test data.

## Installation

```bash
bash build.sh
```

This copies the tool to `~/.cpt`, renames `main.py` to `cpt`, and adds it to your `PATH`.

## Quick Start

Compile the examples and run a comparison:

```bash
g++ examples/aplusb/datagen.cpp -o datagen
g++ examples/aplusb/ac.cpp -o ac
g++ examples/aplusb/wa.cpp -o wa
cpt compare ./datagen ./ac ./wa
```

## Usage

```
cpt <command> [options]
```

Or without installation:

```
python3 main.py <command> [options]
```

## Commands

### compare

Compare two programs by running them on the same generated input.

```
cpt compare <datagen> <program_a> <program_b> [options]
```

| Option | Description |
|---|---|
| `datagen` | Path to the data generator executable |
| `program_a` | Path to program A (reference solution) |
| `program_b` | Path to program B (solution to test) |
| `-s, --strategy` | `nonstop` (default) or `limited_steps` |
| `-m, --mismatch` | Action on mismatch: `stop` (default), `continue`, or `pause` |
| `-c, --caching` | When to cache files: `none`, `mismatches`, `failures`, `both` (default), or `all` |
| `-n, --num-steps` | Number of test cases (default: 10, only for `limited_steps`) |
| `-j, --judger` | Path to judger script (default: `judgers/default.py`) |
| `-t, --max-runtime` | Max runtime in seconds per program (default: `1.0`). Use a tuple `(datagen, progA, progB, judger)` for per-program limits. Set negative for no limit. |
| `-w, --workspace` | Resolve relative file paths against the current workspace instead of `cwd`. |

### cache

Manage cached comparison data.

```
cpt cache list [-n <num>]
cpt cache purge
```

- **`list`** — List all saved cache entries with their ID, creation time, and shell parameters.
- **`purge`** — Clear all cached data.

### dump

Dump cached files to a target directory.

```
cpt dump [cache_id] [-o <target_directory>] [-w]
```

- `cache_id` — Cache ID to dump (defaults to the most recent cache).
- `-o, --output` — Target directory (defaults to the current directory).
- `-w, --workspace` — Resolve `-o` relative to the current workspace.

Dumped files preserve their step subdirectory structure (`1/data.in`, `1/progA.out`, etc.).

### workspace

Manage workspace configuration for resolving relative file paths.

```
cpt workspace set [target_dir] [-w]
cpt workspace disable
```

- **`set`** — Set the workspace root (defaults to current directory).
- **`disable`** — Disable workspace resolution.

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

## Caching

The `-c/--caching` option controls when input/output files are preserved in `~/.cpt/cache/`:

| Value | Files cached when |
|---|---|
| `none` | Never |
| `mismatches` | WA result |
| `failures` | WA, or program/judge execution failure |
| `both` (default) | WA and execution failures |
| `all` | Every step regardless of result |

Use `cpt list` to view cached entries and `cpt dump` to recover files to a working directory.

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

A judger is any executable that reads three CLI arguments (data file, program A output, program B output) and outputs a line starting with `OK`/`AC` to accept or anything else to reject. Compatible with testlib-style judgers. The built-in Python judgers under `judgers/` use the base `lib.Validator` class for convenience.

## Project Structure

```
├── main.py                  # CLI entry point
├── build.sh                 # Installation script
├── lib/
│   ├── __init__.py          # Package marker
│   ├── common/__init__.py   # Subprocess and runtime utilities
│   ├── cache.py             # Cache management (save, list, purge, dump)
│   ├── compare.py           # Core comparison workflow
│   └── workspace.py         # Workspace configuration
├── judgers/
│   ├── default.py           # Default line-by-line judger
│   ├── lib/__init__.py      # Base Validator class and helpers
│   └── ...                  # Other built-in judgers
└── examples/
    ├── aplusb/              # A+B problem (AC, WA, TLE, datagen)
    └── helloworld/          # Hello world (AC, WA variants, datagen)
```
