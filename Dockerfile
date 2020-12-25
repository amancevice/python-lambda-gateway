ARG PYTHON_VERSION=3.8
FROM amazon/aws-lambda-python:${PYTHON_VERSION}
ENV PYTHONPATH=/opt/python:/var/task
EXPOSE 8000
VOLUME /var/task
VOLUME /opt/python
ARG TARBALL=lambda-gateway-latest.tar.gz
COPY ${TARBALL} ${TARBALL}
RUN pip install ${TARBALL} && rm ${TARBALL}
ENTRYPOINT [ "python", "-m", "lambda_gateway" ]
