# TranscribeMe

A Python package for transcription functionality.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Prerequisites

- Python 3.11+
- uv (install from https://docs.astral.sh/uv/getting-started/installation/)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd TranscribeMe

# Install dependencies
make install
# or
uv sync --dev
```

### Development Commands

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Run all checks
make check

# Clean up
make clean
```

### Tools Used

- **uv**: Fast Python package installer and resolver
- **black**: Code formatter
- **ruff**: Fast Python linter
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting

## Project Structure

```
TranscribeMe/
├── src/
│   └── transcribe_me/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── Makefile
└── README.md
```