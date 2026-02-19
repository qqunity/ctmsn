# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CTMSN (Composable Typed Modules for Semantic Networks) is a Python library for working with semantic networks, parametrization, and forcing. The core library has **zero external dependencies** — only Python 3.9+ standard library. It also includes a web UI (Next.js + FastAPI).

## Commands

### Install & Run
```bash
pip3 install -e .                                    # Install in dev mode
python3 src/ctmsn/examples/hello_forcing.py          # Run basic example
python3 src/ctmsn/examples/fast_smith_demo.py        # Run scenario demo
```

### Testing
```bash
python3 tests/test_smoke_imports.py                  # Import smoke tests
python3 tests/test_fast_smith.py                     # Fast Smith scenario tests
python3 -m pytest tests/scenarios/test_fishing_builds.py  # Single scenario test
```

### Web UI (API + Frontend)
```bash
source venv/bin/activate
make install       # Install all deps (API + Web)
make dev           # Run both API (localhost:8000) and Web (localhost:3000)
make dev-api       # Run API only
make dev-web       # Run Web only
make clean         # Stop all dev servers
```

## Architecture

### Core Pipeline

The system follows a consistent flow: **Network → Variables → Constraints → Goal → Runner**

1. **`core/`** — Immutable semantic network primitives: `Concept`, `Predicate`, `Statement`, `SemanticNetwork`
2. **`param/`** — Parametrization layer: `Variable` (with `Domain` constraints), `Context` (partial variable assignments)
3. **`logic/`** — Three-valued logic (`TriBool`: TRUE/FALSE/UNKNOWN) and formulas: `FactAtom`, `EqAtom`, `Not`, `And`, `Or`, `Implies`. `Evaluator` computes formula truth values against a network + context.
4. **`forcing/`** — `ForcingEngine` with `check()` (validate conditions), `forces()` (test if context forces a formula), and `force()` (extend context to satisfy formula — search strategies not yet implemented)
5. **`scenarios/`** — Self-contained reference implementations. Each follows a modular structure: `model.py`, `params.py`, `constraints.py`, `goal.py`, `runner.py`
6. **`examples/`** — Standalone runnable demos
7. **`io/`** — Serialization (stub)

### Apps
- **`apps/api/`** — FastAPI REST backend (FastAPI, Uvicorn, Pydantic)
- **`apps/web/`** — Next.js 15 + React 19 + TypeScript + Tailwind CSS + Cytoscape.js for graph visualization

## Key Conventions

- **Immutability first**: All core data classes use `@dataclass(frozen=True)`. Modifications via `with_*()` methods that return new copies.
- **Always use `from __future__ import annotations`** at the top of source files.
- **Type annotations required** on all public APIs. Use modern syntax: `list[T]`, `dict[K, V]`, `str | None` (not `Optional`). Use `FrozenSet` and `Mapping` for immutable collections.
- **TriBool must never be coerced to bool**. Use explicit checks: `result == TriBool.TRUE`.
- **No mutable default arguments**. Use `field(default_factory=...)`.
- **No external dependencies** in core library code.
- **Absolute imports** for internal modules (e.g., `from ctmsn.core.concept import Concept`).
- **Documentation language is Russian** (README, implementation docs, cursorrules). Code and identifiers are English.
- Documentation style is formal/technical — no emotional expressions, no time estimates, no line-count statistics.
- **After every code edit in `apps/web/` or `apps/api/`**, run the `webapp-testing` skill to verify the changes work correctly in the browser.
- **After each completed feature**, save the written autotest (Playwright script) into `src/tests/` so it can be reused for regression testing.
