# Contributing

## Development Setup

1. Fork the repo and clone locally
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run `make init && make up` to start all services
4. Run `make generate` to populate test data

## Making Changes

- All code and commit messages must be in **English**
- Branch naming: `feature/short-description` or `fix/short-description`
- Run `make test` (dbt tests) before submitting a PR

## Project Layout

```
airflow/dags/       # Airflow DAG — edit pipeline schedule/tasks here
data_generator/     # Faker scripts — edit data shape/volume here
dbt/models/         # dbt SQL models — staging, intermediate, marts
dashboard/pages/    # Streamlit pages — one file per dashboard page
```

## Adding a New dbt Model

1. Create a `.sql` file under the appropriate layer (`staging/`, `intermediate/`, or `marts/`)
2. Add the model to `dbt/models/<layer>/schema.yml` with at minimum `not_null` and `unique` tests on the primary key
3. Run `dbt run --select your_model` to verify it builds
4. Run `dbt test --select your_model` to verify tests pass
