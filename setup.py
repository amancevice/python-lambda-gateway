from setuptools import setup
from setuptools import find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

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
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='lambda-gateway',
    packages=find_packages(exclude=['tests']),
    python_requires='>= 3.7',
    setup_requires=['setuptools_scm'],
    tests_require=[
        'flake8',
        'pytest',
        'pytest-cov',
    ],
    url='https://github.com/amancevice/python-lambda-gateway',
    use_scm_version=True,
)
