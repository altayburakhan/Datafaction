.PHONY: up down init generate test dashboard logs clean

up:
	docker compose up -d

down:
	docker compose down

init:
	docker compose up -d postgres
	docker compose run --rm airflow-init

generate:
	docker compose exec airflow-scheduler python /opt/airflow/data_generator/generate_data.py

test:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt test"

dashboard:
	open http://localhost:8501

airflow:
	open http://localhost:8080

logs:
	docker compose logs -f airflow-scheduler

clean:
	docker compose down -v
	rm -rf dbt/target dbt/dbt_packages airflow/logs
