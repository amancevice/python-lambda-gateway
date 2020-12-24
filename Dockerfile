ARG PYTHON_VERSION=3.8
FROM amazon/aws-lambda-python:${PYTHON_VERSION}
ENV PYTHONPATH=/opt/python:/var/task
EXPOSE 8000
VOLUME /var/task
VOLUME /opt/python
COPY dist .
RUN pip install *.tar.gz && rm *.tar.gz
ENTRYPOINT [ "python", "-m", "lambda_gateway" ]
