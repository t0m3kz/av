# Spatium

A FastAPI application for analyzing network device configurations and deploying digital twins, with a focus on SONiC OS.

## Features

- Retrieve device configurations via SSH or gNMI
- Analyze configurations using Batfish
- Deploy digital twins using ContainerLab
- REST API for integration with other tools

## Installation

```bash
uv pip install -e .
uv pip install -e ".[dev]"
```

## Running

```bash
uvicorn main:app --reload
```

## Testing

```bash
uv run pytest
```

## Linting & Formatting

```bash
uv run ruff format .
uv run ruff check .
```

## Documentation

```bash
mkdocs serve
```
Documentation will be available at [http://localhost:8000](http://localhost:8000) by default.

## Configuration

See `.env.example` for all available environment variables.

---

For more details, see the [full documentation](docs/index.md).