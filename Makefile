PYTHON ?= $(shell \
	python3 -c 'import pytest, pyomo' >/dev/null 2>&1 && echo python3 \
	|| { [ -x "$$HOME/Documents/Projects/Protime/planning-calculation-service/.venv/bin/python" ] \
		&& echo "$$HOME/Documents/Projects/Protime/planning-calculation-service/.venv/bin/python"; } \
	|| echo python3)

.PHONY: test step1 step2 step3 step4 step5 rooster
test:
	$(PYTHON) -m pytest

step1 step2 step3 step4 step5:
	PYTHONPATH=src $(PYTHON) -m workshop.show $(subst step,,$@)

rooster:
	PYTHONPATH=src $(PYTHON) -m workshop.show rooster
