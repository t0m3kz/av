# Spatium

A FastAPI application for retrieving network device configurations (SONiC OS) via SSH or gNMI.

## Features

- Retrieve device configurations via SSH or gNMI
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
# Removed Batfish/config analysis support. Only SSH/gNMI config retrieval and digital twin deployment remain.