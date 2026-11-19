.PHONY: test step1 step2 step3 step4 step5 rooster
test:
	uv run pytest

step1 step2 step3 step4 step5:
	PYTHONPATH=src uv run python -m workshop.show $(subst step,,$@)

rooster:
	PYTHONPATH=src uv run python -m workshop.show rooster
