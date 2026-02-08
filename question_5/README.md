# Shipay Challenge Service

FastAPI service for user creation flow, built with full async support.

### Prerequisites

- Docker / Docker Compose

### Local Environment Setup

| Command                         | Purpose                                                       |
|---------------------------------|---------------------------------------------------------------|
| `make build`                    | Docker compose up --build (recreates image + containers)      |
| `make up`                       | Start stack (API, DB)                                         |
| `make down`                     | Stop and clean containers                                     |


```
# API available at http://localhost:8000/
```

## Database & Migrations

| Command                         | Purpose                                                       |
|---------------------------------|---------------------------------------------------------------|
| `make migrations`               | autogenerate new revision from models                         |
| `make migrate`                  | apply latest revision (upgrade head)                          |


## Testing & Quality Gates

| Command                         | Purpose                                                       |
|---------------------------------|---------------------------------------------------------------|
| `make test`                     | Shortcut for `pytest` (uses current venv)                     |
| `make ruff`                     | Fix import order + format using Ruff                          |
