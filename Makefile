.PHONY: setup dry-run status check test

setup:
	./setup

dry-run:
	./setup --dry-run

status:
	./setup --status

check:
	python3 scripts/check_codex_setup.py

test:
	python3 -m pytest -q
