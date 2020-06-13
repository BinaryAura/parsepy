from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="parsepy",
    version="0.5.1",
    author="BinaryAura",
    author_email="jadunker@hotmail.com",
    description="A run-time parser with semantics and interpretation features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BinaryAura/parsepy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=[
        "parsepy",
        "parsepy.lexer",
        "parsepy.parser"
    ],
    python_requires='>3.7'
)
