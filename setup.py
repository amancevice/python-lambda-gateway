from setuptools import find_packages
from setuptools import setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    author='amancevice',
    author_email='smallweirdnum@gmail.com',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
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
    python_requires='>= 3.8',
    setup_requires=['setuptools_scm'],
    tests_require=[
        'flake8',
        'pytest',
        'pytest-cov',
    ],
    url='https://github.com/amancevice/python-lambda-gateway',
    use_scm_version=True,
)
