# Contributing to FastArch

Thank you for your interest in contributing! We welcome bug reports, feature requests, and pull requests.

## How to Report a Bug

1. Check existing [GitHub Issues](https://github.com/yourusername/fastarch/issues) to avoid duplicates
2. Open a new issue with:
   - Clear title describing the bug
   - Minimal reproduction code
   - Python version, FastAPI version
   - Expected vs actual behavior

## How to Request a Feature

1. Check existing [GitHub Discussions](https://github.com/yourusername/fastarch/discussions)
2. Describe the use case and motivation
3. Propose an API design if possible

## How to Contribute Code

### Setup

```bash
make setup-dev
```

### Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and commit with clear messages
4. Add or update tests for your changes
5. Ensure all tests pass:
   ```bash
   make test
   make lint
   ```

### Code Quality

- **Type hints**: All code must have complete type annotations
- **Docstrings**: Public functions/classes need docstrings (Google style)
- **Tests**: New features require tests with >90% coverage
- **Formatting**: Use `make format` before committing

### Pull Request Process

1. Ensure CI passes (GitHub Actions)
2. Update `CHANGELOG.md` under `[Unreleased]` section
3. Write a clear PR description:
   - Why this change?
   - What does it do?
   - Any breaking changes?
4. Request review from maintainers

## Development Workflow

```bash
# Run all checks
make test && make lint

# Auto-format code
make format

# Watch tests
make test-watch

# Clean cache
./clean.sh
```

## Code Style Guidelines

- **Imports**: Use `from __future__ import annotations` for forward references
- **Dataclasses**: Use `frozen=True, slots=True` for immutable metadata classes
- **Decorators**: Keep decorators as pure metadata holders (don't wrap)
- **Tests**: Use pytest, one assertion per test preferred

## Documentation

- Keep `docs/` updated for major features
- Update `CHANGELOG.md` for releases
- Docstrings should include:
  - One-line summary
  - Detailed description if needed
  - Args and Returns (with types)
  - Raises section if applicable
  - Example usage

## Release Process

Maintainers only:

1. Update version in `fastarch/__version__.py`
2. Update `CHANGELOG.md`: move `[Unreleased]` to version heading
3. Commit: `git commit -m "Release v0.2.0"`
4. Tag: `git tag -a v0.2.0 -m "Release version 0.2.0"`
5. Push: `git push --tags`
6. Build and publish: `make publish` (if implemented)

## Questions?

- Open a Discussion in GitHub
- Check existing issues and tests for examples
- Review `docs/explain/overview.md` for architecture overview

Thank you for contributing! 🙏
