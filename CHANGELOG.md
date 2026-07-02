# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-02

### Added
- Initial MVP release of FastArch
- `@controller()` decorator for class-based controller registration
- `@route()` decorator and HTTP method shortcuts (`@get`, `@post`, `@put`, `@patch`, `@delete`)
- Support for `guards` (authorization/security dependencies) separate from regular `dependencies`
- `include_controllers()` function to register controllers on FastAPI apps
- Full type hints and support for Python 3.10+
- Comprehensive test suite covering metadata, registry, and FastAPI compatibility
- Example FastAPI backend with authentication guards

### Design Decisions
- **Metadata-first approach**: Decorators only store metadata without wrapping functions
- **Guard separation**: Guards are tracked separately from dependencies for semantic clarity
- **Order preservation**: Dependencies and guards execute in controller → route order
- **FastAPI native**: Uses FastAPI's native `APIRouter` and `Depends()` for integration

### Known Limitations
- Requires FastAPI >= 0.115
- Only tested with class-based controllers (instance or zero-arg classes)
- Sync and async endpoints both supported but not explicitly tested in edge cases

---

For detailed API documentation, see [docs/api.md](docs/api.md).
For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
