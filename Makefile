SDIST   := dist/$(shell python setup.py --fullname).tar.gz
SLEEP   := 0
TIMEOUT := 3

.PHONY: default clean up upload

default: $(SDIST)

clean:
	rm -rf dist

upload: $(SDIST)
	twine upload $<

up:
	SLEEP=$(SLEEP) python -m lambda_gateway -t $(TIMEOUT) lambda_function.lambda_handler

$(SDIST):
	python setup.py sdist
