fmt:
	ruff check --select I --fix solution/
	ruff format solution/ --no-cache
	@echo '[OK] Formatters went through successfully'

lint:
	ruff check solution --no-cache
	@echo '[OK] Linters checks passed successfully'

run:
	uvicorn solution.main:app --reload

test:
	pytest test -s

test-fast:
	pytest test -s -m "not slow"
