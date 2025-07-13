# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pytoolkit-result is a Rust-inspired Result and Option type implementation for Python. It provides type-safe error handling and optional value management through functional programming patterns. The library prioritizes practical usability over complete Rust specification compliance.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install development dependencies  
uv sync --group dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test class
uv run pytest tests/test_result.py::TestOk

# Run single test method
uv run pytest tests/test_result.py::TestOk::test_unwrap -v

# Run tests with coverage
uv run pytest --cov=pytoolkit_result
```

### Code Quality
```bash
# Type checking (strict mode enabled)
uv run pyright

# Linting
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix

# Code formatting
uv run ruff format

# Run all quality checks
uv run pyright && uv run ruff check && uv run ruff format
```

### Building
```bash
# Build package
uv build
```

## Architecture Overview

### Module Structure
- `pytoolkit_result/result.py`: Core Result and Option type implementations
- `pytoolkit_result/option.py`: Option-specific types (Some, Nothing)
- `pytoolkit_result/__init__.py`: Public API exports

### Type Hierarchy
```
Result[T, E] (abstract)
├── Ok[T, E] - Success case with value of type T
└── Err[T, E] - Error case with error of type E

Option[T] (abstract)  
├── Some[T] - Contains value of type T
└── Nothing[T] - Empty/None case
```

### Key Design Principles

1. **Complete Abstraction**: The `Result` and `Option` base classes contain only abstract methods. All concrete behavior is implemented in `Ok`/`Err` and `Some`/`Nothing` respectively.

2. **Type Safety Priority**: Uses generic types with TypeVar for compile-time type safety. The `UnwrapError` exception provides consistent error handling regardless of stored error types.

3. **Rust-Inspired API**: Methods like `map()`, `and_then()`, `unwrap()`, `unwrap_or()`, `expect()`, `map_err()`, etc. follow Rust conventions.

### Critical Implementation Decisions

#### Simplified `and_then` Signature
The library uses a simplified type signature for `and_then`:
- **Rust**: `fn and_then<U, F>(self, op: FnOnce(T) -> Result<U, F>) -> Result<U, F> where F: From<E>`
- **Python**: `def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]`

This preserves error types in 90%+ of use cases while avoiding complex type conversion machinery. For error type conversion, use `map_err()` explicitly.

#### UnwrapError Exception Strategy
`Err.unwrap()` always raises `UnwrapError` regardless of the stored error type. The original error value is accessible via `error_value` attribute. This ensures consistent behavior when `E` is not an Exception subclass.

#### Result[T, E] vs Result[T]
The implementation uses `Result[T, E]` (two type parameters) to match Rust's design, allowing different error types like `Result[int, str]` or `Result[Option[int], ValueError]`.

## Testing Patterns

### Test Organization
- Tests are organized by class: `TestOk`, `TestErr`, `TestSome`, `TestNothing`
- Comprehensive coverage includes edge cases, type combinations, and method chaining
- Special test classes for advanced features: `TestUnwrapError`, `TestComplexTypes`

### Common Test Patterns
```python
# Type-annotated error creation
err: Err[int, ValueError] = Err(ValueError("test"))

# Complex type testing  
result: Result[Option[int], str] = Ok(Some(42))

# Exception testing with UnwrapError
with pytest.raises(UnwrapError) as exc_info:
    err.unwrap()
assert exc_info.value.error_value is original_error
```

## API Compatibility Notes

### Import Patterns
```python
# Recommended imports
from pytoolkit_result import Result, Ok, Err, Option, Some, Nothing, UnwrapError

# Type hints
def process_data(data: str) -> Result[int, ValueError]:
    try:
        return Ok(int(data))
    except ValueError as e:
        return Err(e)
```

### Method Chaining
The API is designed for fluent method chaining:
```python
result = (Ok(10)
    .map(lambda x: x * 2)
    .and_then(lambda x: Ok(x + 5) if x > 0 else Err("negative"))
    .map_or_else(lambda err: f"Error: {err}", lambda x: f"Success: {x}"))
```

## Implementation History and Design Decisions

### Key Design Evolution

#### Result[T, E] Type System Implementation
- **Initial Challenge**: Needed to support complex types like `Result[Option[int], str]`
- **Solution**: Implemented two-parameter generic `Result[T, E]` to match Rust's design
- **Impact**: Enables type-safe error handling with custom error types beyond Exception

#### and_then Method Type Signature Decision
- **Problem**: Rust's full signature `fn and_then<U, F>(self, op: FnOnce(T) -> Result<U, F>) -> Result<U, F> where F: From<E>` would require complex type conversion machinery in Python
- **Decision**: Simplified to `def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]`
- **Rationale**: 
  - Covers 90%+ of real-world usage patterns where error type is preserved
  - Avoids Python type system limitations
  - Explicit error type conversion available via `map_err()`
- **Documentation**: Extensively documented in method docstring and module-level comments

#### UnwrapError Exception Strategy
- **Problem**: `Err.unwrap()` needed to handle cases where `_error` is not an Exception subclass
- **Initial Approach**: Conditional logic to check `isinstance(self._error, Exception)`
- **Final Decision**: Always raise `UnwrapError` regardless of error type
- **Benefits**:
  - Consistent behavior across all error types
  - Original error preserved in `error_value` attribute
  - Type-safe operation when `E` is `str`, `int`, or custom types

#### Abstract Base Class Design
- **Principle**: Result class contains zero concrete implementations
- **Rationale**: 
  - Forces consistent implementation in Ok/Err subclasses
  - Prevents inheritance confusion
  - Improves debugging and type checking
- **Implementation**: All methods including `__iter__()` are abstract and implemented in subclasses

#### cast() Usage Considerations
- **Context**: During `Err.map()` implementation, discussed whether to use `cast()` or create new instances
- **Decision**: Use new instance creation (`Err[U, E](self._error)`) over `cast(Err[U, E], self)`
- **Reasoning**: Prioritizes code clarity and type consistency over minor performance gains

### Testing Strategy Evolution
- **Comprehensive Coverage**: 72 test cases covering all methods and edge cases
- **Type-Specific Testing**: Tests for `Result[Option[int], str]` and other complex type combinations
- **Error Handling Validation**: Dedicated `TestUnwrapError` class for exception behavior
- **Method Chaining**: Complex chaining scenarios to validate functional programming patterns

## Versioning and Dependencies

- Uses date-based versioning: `vYYYY.MM.DD.XX`
- Requires Python 3.13+
- No runtime dependencies
- Development dependencies: pyright, pytest, ruff