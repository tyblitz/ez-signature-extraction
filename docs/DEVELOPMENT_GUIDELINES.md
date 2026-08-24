# Development Guidelines

## Overview

This document provides guidelines for developing EZ Version 1, ensuring code quality, consistency, and maintainability.

---

## Coding Standards

### Python Version

- **Target:** Python 3.8+
- **Style:** Follow PEP 8 guidelines
- **Type Hints:** Required for all function signatures

### Type Hints

Always use type hints for better code documentation and IDE support:

```python
# Good
def process_image(path: str) -> Image.Image:
    ...

# Bad
def process_image(path):
    ...
```

### Function Documentation

Every function must have a docstring:

```python
def refine_signature(extraction_result: ExtractionResult) -> RefinementResult:
    """
    Remove paper background and preserve signature strokes.
    
    Args:
        extraction_result: Result from Module 3 containing extracted signature
    
    Returns:
        RefinementResult with transparent signature
        
    Raises:
        TypeError: If extraction_result is not ExtractionResult
    """
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `detect_signature()` |
| Classes | PascalCase | `DetectionResult` |
| Constants | UPPER_SNAKE_CASE | `BLUE_HUE_MIN` |
| Variables | snake_case | `signature_mask` |

---

## Architecture Guidelines

### Immutability

Never modify input data. Always work on copies:

```python
# Good
working_copy = original_image.copy()
process(working_copy)

# Bad
original_image.paste(...)  # Modifies input
```

### Single Responsibility

Each function should have one clear purpose:

```python
# Good - Separate concerns
def detect_blue_ink(image): ...
def detect_background(image): ...
def remove_background(ink, background): ...

# Bad - Multiple responsibilities
def detect_and_remove(image): ...
```

### Result Objects

Use immutable Result objects for error handling:

```python
@dataclass(frozen=True)
class Result:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
```

---

## Testing Guidelines

### Test Structure

```python
import unittest
from backend.module import function

class TestModuleFunction(unittest.TestCase):
    def test_normal_case(self):
        """Test typical usage."""
        result = function(input)
        self.assertTrue(result.success)
        
    def test_edge_case(self):
        """Test edge conditions."""
        result = function(edge_input)
        self.assertTrue(result.success)
        
    def test_error_case(self):
        """Test error handling."""
        result = function(invalid_input)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
```

### Test Coverage

Target: 100% coverage for critical paths

Run tests with:
```bash
python -m unittest discover -s backend/tests
```

### Test Categories

1. **Input Validation Tests** - Invalid inputs
2. **Functional Tests** - Normal operation
3. **Edge Case Tests** - Boundary conditions
4. **Integration Tests** - Module interactions
5. **Performance Tests** - Speed requirements

---

## Color Detection Guidelines

### LAB Color Space for Background

```python
# Background detection
lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
l_channel = lab[:, :, 0] / 255.0
b_channel = (lab[:, :, 2] - 128) / 127.0

is_background = (l_channel > 0.80) & (b_channel > 0.05)
```

### HSV Color Space for Blue Ink

```python
# Blue ink detection
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
h = hsv[:, :, 0] / 179.0  # Normalize to 0-1
s = hsv[:, :, 1] / 255.0

is_blue = (h >= 0.47) & (h <= 0.75) & (s > 0.10)
```

---

## Performance Guidelines

### Memory Efficiency

```python
# Good - Use numpy arrays for efficient processing
arr = np.array(image)
result = arr[:, :, 0] > 128

# Bad - Nested loops
for y in range(height):
    for x in range(width):
        ...
```

### Algorithm Complexity

| Operation | Target | Notes |
|-----------|--------|-------|
| Image loading | O(n) | n = pixels |
| Color detection | O(n) | Single pass |
| Connected components | O(n) | OpenCV optimized |
| Distance transform | O(n) | OpenCV optimized |

### Benchmarks

```python
import time

start = time.time()
result = process_image(path)
elapsed = time.time() - start

assert elapsed < 2.0, f"Processing took {elapsed}s"
```

---

## Version Control

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-new-detection

# Make changes
git add .
git commit -m "Add blue ink detection using HSV"

# Push and create PR
git push origin feature/add-new-detection
```

### Commit Messages

```
feat: Add blue ink detection using HSV

- Implement HSV-based blue detection
- Add saturation threshold
- Update tests

Refs: #123
```

### Branch Naming

- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation
- `test/*` - Test improvements

---

## Documentation Standards

### Docstrings

Use Google-style docstrings:

```python
def process_image(
    path: str,
    output_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """Process an image and extract signature.
    
    Args:
        path: Path to input image
        output_dir: Optional output directory
    
    Returns:
        Tuple of (success, message)
    
    Example:
        >>> success, msg = process_image('doc.jpg')
        >>> print(msg)
    """
```

### README Updates

Update README.md when:
- Adding new features
- Changing requirements
- Updating installation

---

## Debugging Guidelines

### Print Debugging

Use print statements during development:

```python
print(f"[DEBUG] Blue pixels: {np.sum(blue_mask)}")
print(f"[DEBUG] Background: {np.sum(background_mask)}")
```

### Logging (Future)

Will use Python logging module in v1.1+

---

## Code Review Checklist

- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Tests added/updated
- [ ] No new warnings
- [ ] Performance acceptable
- [ ] Follows PEP 8
- [ ] No hardcoded paths

---

## Dependencies

### Allowed

- Pillow >= 9.0.0
- OpenCV >= 4.5.0
- NumPy >= 1.20.0

### Forbidden

- TensorFlow, PyTorch
- Machine learning libraries
- Cloud APIs
- External services

---

## Release Checklist

Before tagging a release:

- [ ] All tests pass (103 tests)
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number updated
- [ ] Performance validated
- [ ] Edge cases tested