setup:
	$(PYTHON_CMD) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python src/manage.py runserver

migrate:
	.venv/bin/python src/manage.py migrate

createsuperuser:
	.venv/bin/python src/manage.py createsuperuser

test:
	.venv/bin/python -m unittest discover tests

freeze:
	.venv/bin/pip freeze > requirements.txt

clean:
	rm -rf __pycache__ *.pyc .venv
