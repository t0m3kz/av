# Contributing to Spatium

Thank you for considering contributing to Spatium! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/spatium.git
   cd spatium
   ```
3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. Make your changes and write tests
2. Run the tests:
   ```bash
   pytest
   ```
3. Format your code:
   ```bash
   black .
   isort .
   ```
4. Check for linting errors:
   ```bash
   flake8
   ```
5. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a pull request on GitHub

## Code Style

We follow these coding standards:

- [Black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [Flake8](https://flake8.pycqa.org/) for linting
- [MyPy](https://mypy.readthedocs.io/) for type checking

## Testing

Write tests for all new features and bug fixes. We use pytest for testing.

- Unit tests go in `tests/unit/`
- Integration tests go in `tests/integration/`
- Run tests with `pytest`

## Documentation

Update documentation for any new features or changes:

1. Update API documentation in `docs/api/`
2. Update user guides in `docs/user-guide/`
3. Build documentation with `mkdocs serve` to preview changes
4. Build for deployment with `mkdocs build`

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add yourself to CONTRIBUTORS.md if you're not already listed
4. Submit your pull request
5. Address any review comments

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Be patient with new contributors

Thank you for contributing to Spatium!