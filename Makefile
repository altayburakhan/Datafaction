.PHONY: up down init generate test dashboard logs clean

up:
	docker compose up -d

down:
	docker compose down

init:
	cp .env.example .env
	@python3 -c "import base64,os; f=open('.env','r+'); c=f.read(); f.seek(0); f.write(c.replace('YOUR_FERNET_KEY_HERE', base64.urlsafe_b64encode(os.urandom(32)).decode()).replace('YOUR_SECRET_KEY_HERE', base64.urlsafe_b64encode(os.urandom(32)).decode())); f.truncate()"
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
