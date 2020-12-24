SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: all clean test up upload

all: $(SDIST)

clean:
	rm -rf dist

test: coverage.xml

upload: $(SDIST)
	twine upload $<

up:
	SLEEP=$(SLEEP) python -m lambda_gateway -t $(TIMEOUT) lambda_function.lambda_handler

coverage.xml: $(shell find lambda_gateway tests -name '*.py')
	flake8 $^
	pytest

$(SDIST): coverage.xml
	python setup.py sdist
