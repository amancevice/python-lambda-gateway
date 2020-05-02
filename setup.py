from setuptools import setup
from setuptools import find_packages

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    description='Simple HTTP server to invoke a Lambda function locally',
    entry_points={
        'console_scripts': [
            'lambda-gateway=lambda_gateway.server:main',
        ],
    },
    install_requires=[],
    name='lambda-gateway',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    tests_require=[
        'flake8',
        'pytest',
        'pytest-cov',
    ],
    url='https://github.com/amancevice/python-lambda-gateway',
    use_scm_version=True,
)
