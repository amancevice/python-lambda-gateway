REPO    := amancevice/lambda-gateway-python
SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: all clean images push test up upload

all: dist/lambda-gateway-latest.tar.gz

clean:
	rm -rf dist *.iid .pytest_cache coverage.xml

images: Dockerfile.3.7.iid Dockerfile.3.8.iid

push: Dockerfile.3.7.iid Dockerfile.3.8.iid
	docker push --all-tags $(REPO)

test: coverage.xml

up:
	SLEEP=$(SLEEP) python -m lambda_gateway -t $(TIMEOUT) lambda_function.lambda_handler

upload: $(SDIST)
	twine upload $<

Dockerfile.%.iid: dist/lambda-gateway-latest.tar.gz Dockerfile
	docker build \
	--build-arg PYTHON_VERSION=$* \
	--build-arg TARBALL=$< \
	--iidfile $@ \
	--tag $(REPO):$* \
	.

dist/lambda-gateway-latest.tar.gz: $(SDIST)
	cp $< $@

dist/lambda-gateway-%.tar.gz: coverage.xml
	SETUPTOOLS_SCM_PRETEND_VERSION=$* python setup.py sdist

coverage.xml: $(shell find lambda_gateway tests -name '*.py')
	pytest
