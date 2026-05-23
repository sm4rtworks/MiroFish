```markdown
# MiroFish Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the MiroFish Python repository. You'll learn how to structure files, write imports and exports, follow commit message guidelines, and understand the project's testing approach. These patterns ensure consistency, readability, and maintainability across the codebase.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `miro_fish_utils.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import calculate_fish_population
    ```

### Export Style
- Use **named exports** by explicitly listing exported functions or classes.
  - Example:
    ```python
    __all__ = ['calculate_fish_population', 'FishTank']
    ```

### Commit Messages
- Follow **conventional commit** format.
- Use the `chore` prefix for routine tasks.
  - Example:
    ```
    chore: update dependencies for compatibility
    ```

## Workflows

### Code Update
**Trigger:** When making changes or improvements to the codebase  
**Command:** `/code-update`

1. Make your code changes following the coding conventions.
2. Use relative imports and named exports as needed.
3. Write a commit message using the `chore` prefix and a concise description.
   - Example: `chore: refactor fish tank initialization logic`
4. Commit and push your changes.

### Testing
**Trigger:** When adding or modifying code that requires validation  
**Command:** `/run-tests`

1. Create or update test files using the `*.test.*` naming pattern.
   - Example: `fish_population.test.py`
2. Write test cases to cover new or changed functionality.
3. Run your tests using the project's preferred method (testing framework is currently unknown).
4. Ensure all tests pass before merging changes.

## Testing Patterns

- Test files are named using the `*.test.*` pattern.
  - Example: `fish_population.test.py`
- The specific testing framework is not specified; follow the existing patterns in test files.
- Place tests alongside the code they validate or in a dedicated test directory if present.

## Commands
| Command         | Purpose                                      |
|-----------------|----------------------------------------------|
| /code-update    | Apply code changes following conventions     |
| /run-tests      | Run all test files matching `*.test.*`       |
```