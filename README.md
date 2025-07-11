# pytoolkit-template

pytoolkit template project

## Requirements

- Python 3.13+
- uv (for dependency management)

## Installation

```bash
uv sync
```

## Development

Install development dependencies:

```bash
uv sync --group dev
```

Run tests:

```bash
uv run pytest
```

Run type checking:

```bash
uv run pyright
```

Run linting:

```bash
uv run ruff check
```

Fix linting issues:

```bash
uv run ruff check --fix
```

Format code:

```bash
uv run ruff format
```

## Build

```bash
uv build
```
