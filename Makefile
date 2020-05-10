SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: default clean upload

default: $(SDIST)

clean:
	rm -rf dist

upload: $(SDIST)
	twine upload $<

up:
	SLEEP=$(SLEEP) python -m lambda_gateway.server -t $(TIMEOUT) -B simple lambda_function.lambda_handler

$(SDIST):
	python setup.py sdist
