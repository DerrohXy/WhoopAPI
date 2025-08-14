install:
	venv/bin/python3 -m pip install -r requirements.txt

test:
	venv/bin/python3 -m unittest discover

format:
	venv/bin/python3 -m isort .
	venv/bin/python3 -m black .
	venv/bin/python3 -m flake8 .

