.PHONY: setup dry-run status check doctor stack test reverify

setup:
	./setup

dry-run:
	./setup --dry-run

status:
	./setup --status

check:
	python3 scripts/check_codex_setup.py
	python3 scripts/check_stack.py

doctor: check

stack:
	python3 scripts/check_stack.py --list

reverify:
	python3 scripts/reverify_stack_pin.py

test:
	pytest -q
