SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: default clean test up upload

default: $(SDIST)

clean:
	rm -rf dist

test:
	py.test

upload: $(SDIST)
	twine upload $<

up:
	SLEEP=$(SLEEP) python -m lambda_gateway -t $(TIMEOUT) lambda_function.lambda_handler

$(SDIST): test
	python setup.py sdist
