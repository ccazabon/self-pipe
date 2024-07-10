SOURCE_DIRECTORIES = ./self_pipe

format:
	isort $(SOURCE_DIRECTORIES)
	black $(SOURCE_DIRECTORIES)

lint:
	isort --check-only $(SOURCE_DIRECTORIES)
	black --check $(SOURCE_DIRECTORIES)
	flake8 $(SOURCE_DIRECTORIES)
	mypy $(SOURCE_DIRECTORIES)
