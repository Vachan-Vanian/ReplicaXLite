# ReplicaXLite Contribution Guidelines

## Overview
Thanks for contributing to ReplicaXLite! Follow these guidelines to keep our code consistent and maintainable.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/replicaxlite.git`
3. Create a new branch: `git checkout -b feature/name-your-feature`
4. Make your changes
5. Test your changes
6. Push and submit a Pull Request

## Development Setup

```bash
# Create environment
conda create -n replicax-dev python=3.11.9
conda activate replicax-dev

# Install in development mode
pip install -e . --config-settings editable_mode=strict

```

## Branch Naming

Format: `<type>/<issue-number>-brief-description`

**Types:** `feature`, `bugfix`, `docs`, `refactor`, `test`, `chore`

**Examples:**
```
feature/123-add-new-feature
bugfix/456-fix-render-issue
docs/789-update-readme
```

## Commit Messages

Format: `<type>(<scope>): <subject>`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat(api): add support for feature X
fix(gui): resolve viewport rendering glitch
docs(readme): update installation instructions
test(api): add unit tests for node creation
```

Keep it short and use imperative mood ("add" not "added").

## Code Style

### Python Guidelines
- Follow [PEP 8](https://pep8.org/)
- Max line length: 88 characters
- Use type hints for functions
- Add docstrings for functions/classes

### Naming
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

### Example
```python
from typing import List

def example_function(param1: str, param2: int = 0) -> List[str]:
    """Brief description of what this function does.
    
    Args:
        param1: Description of the first parameter
        param2: Description of optional parameter with default value
        
    Returns:
        Description of what the function returns
        
    Raises:
        ValueError: When invalid input is provided
    """
    pass
```

## Testing

- Add tests for new features
- Ensure all existing tests pass

**Example test:**
```python
def test_example_feature():
    """Test description of what is being tested."""
    # Arrange - set up test data
    input_value = "test_input"
    expected_output = "expected_result"
    
    # Act - call the function
    result = example_function(input_value)
    
    # Assert - verify the result
    assert result == expected_output
```

## Pull Requests

### Title
`<type>: Brief description`

Example: `feat: Add support for feature X`

### Description Template
```markdown
## Summary
What this PR does and why.

## Changes
- Added feature X
- Fixed bug Y
- Updated docs for Z

## Testing
How you tested: unit tests, manual testing, etc.

## Related Issues
Closes #123
```

### Checklist
- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No linting errors

## Reporting Issues

### Bug Reports
Include:
- ReplicaXLite version
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Error messages/screenshots

### Feature Requests
Describe:
- The problem you're solving
- Your proposed solution
- Any mockups or examples

## Review Process

1. Submit PR
2. Wait for review
3. Address feedback
4. Get approval and merge

---

## Questions?

- Check [documentation](docs/)
- Search [issues](https://github.com/Vachan-Vanian/replicaxlite/issues)
- Email: [vachanvanian@outlook.com](mailto:vachanvanian@outlook.com)

Thanks for contributing! 🎉

*Last updated: October 11, 2025*