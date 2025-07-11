# pytoolkit-result

Rust-inspired Result type for Python with type safety and functional programming features.

## Overview

This library provides a `Result[T]` type that represents either a successful value (`Ok[T]`) or an error (`Err[T]`). It's designed to make error handling more explicit and type-safe by avoiding exceptions for expected error conditions.

## Features

- **Type-safe error handling**: Explicit handling of success and error cases
- **Functional programming support**: Map and bind operations for chaining computations
- **Abstract base class**: Prevents direct instantiation of Result
- **Rust-inspired API**: Familiar interface for Rust developers

## Requirements

- Python 3.13+
- uv (for dependency management)

## Installation

```bash
uv sync
```

## Usage

### Basic Usage

```python
from pytoolkit_result.result import Ok, Err, Result

# Create success result
success: Result[int] = Ok(42)
print(success.is_ok())        # True
print(success.unwrap())       # 42
print(success.unwrap_or(0))   # 42

# Create error result
error: Result[int] = Err(ValueError("Something went wrong"))
print(error.is_ok())          # False
print(error.unwrap_or(0))     # 0
# error.unwrap()              # Raises ValueError
```

### Functional Operations

```python
# Map operation - transform the value if Ok
result = Ok(10).map(lambda x: x * 2)
print(result.unwrap())  # 20

# Map on Err returns the same Err
error_result = Err[int](ValueError("error")).map(lambda x: x * 2)
print(error_result.is_error())  # True

# Chain operations with and_then
def divide_by_two(x: int) -> Result[float]:
    return Ok(x / 2.0)

def to_string(x: float) -> Result[str]:
    return Ok(str(x))

result = Ok(10).and_then(divide_by_two).and_then(to_string)
print(result.unwrap())  # "5.0"
```

### Error Handling Patterns

```python
def safe_divide(a: int, b: int) -> Result[float]:
    if b == 0:
        return Err[float](ValueError("Division by zero"))
    return Ok(a / b)

# Handle the result
result = safe_divide(10, 2)
if result.is_ok():
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.unwrap_or(0)}")

# Or use unwrap_or for default values
value = safe_divide(10, 0).unwrap_or(0.0)
print(value)  # 0.0
```

### Method Chaining

```python
# Chain multiple operations
result = (Ok(100)
    .map(lambda x: x // 2)        # 50
    .and_then(lambda x: Ok(x - 10) if x > 10 else Err[int](ValueError("Too small")))  # 40
    .map(lambda x: x * 2))        # 80

print(result.unwrap())  # 80
```

## API Reference

### Result[T] (Abstract Base Class)

- `is_ok() -> bool`: Returns True if this is an Ok value
- `is_error() -> bool`: Returns True if this is an Err value  
- `unwrap() -> T`: Returns the value or raises the error
- `unwrap_or(default: T) -> T`: Returns the value or the default
- `map(f: Callable[[T], U]) -> Result[U]`: Transform the value if Ok
- `and_then(f: Callable[[T], Result[U]]) -> Result[U]`: Chain Result-returning operations

### Ok[T]

Represents a successful result containing a value of type T.

### Err[T]

Represents an error result containing an exception.

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

## License

This project is licensed under the MIT License.