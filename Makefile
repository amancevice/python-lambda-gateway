SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: default clean test up upload

default: $(SDIST)

clean:
	rm -rf dist

test: coverage.xml

upload: $(SDIST)
	twine upload $<

up:
	SLEEP=$(SLEEP) python -m lambda_gateway -t $(TIMEOUT) lambda_function.lambda_handler

coverage.xml: $(shell find . -name '*.py' -not -path './.*')
	flake8 $^
	pytest

$(SDIST): coverage.xml
	python setup.py sdist
