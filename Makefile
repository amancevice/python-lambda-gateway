REPO    := amancevice/lambda-gateway-python
SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: all clean test up upload

all: Dockerfile.3.8.iid Dockerfile.3.7.iid

clean:
	rm -rf dist *.iid coverage.xml

test: coverage.xml

up:
	SLEEP=$(SLEEP) python -m lambda_gateway -t $(TIMEOUT) lambda_function.lambda_handler

upload: $(SDIST)
	twine upload $<

Dockerfile.%.iid: $(SDIST) Dockerfile
	docker build \
	--build-arg PYTHON_VERSION=$* \
	--iidfile $@ \
	--tag $(REPO):$* \
	.

$(SDIST): coverage.xml
	python setup.py sdist

coverage.xml: $(shell find lambda_gateway tests -name '*.py')
	flake8 $^
	pytest
