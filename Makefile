SOURCE_DIRECTORIES=./self_pipe
PYTEST_OPTIONS="-vv"


format:
	isort $(SOURCE_DIRECTORIES)
	black $(SOURCE_DIRECTORIES)

lint:
	isort --check-only $(SOURCE_DIRECTORIES)
	black --check $(SOURCE_DIRECTORIES)
	flake8 $(SOURCE_DIRECTORIES)
	mypy $(SOURCE_DIRECTORIES)

test:
	pytest $(PYTEST_OPTIONS) 2>&1 | decolourize | strip-nuls | tee run-tests.log

test-interactive:
	pytest $(PYTEST_OPTIONS) --pdb

setup-repo:
	poetry source add --priority supplemental pyropus http://hex.pyropus.ca:8080/

publish:
	poetry publish --build --repository pyropus

