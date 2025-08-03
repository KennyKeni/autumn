.PHONY: fix

fix:
	uv run autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src
	uv run isort src
	uv run black src