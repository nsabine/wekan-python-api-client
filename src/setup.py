from setuptools import setup
from pip.download import PipSession
from pip.req import parse_requirements

setup(
    name="wekanapi",
    description="Wekan Python API client",
    version="0.0.1",
    packages=["wekanapi"],
    install_requires=[str(requirement.req) for requirement in parse_requirements('requirements.txt', session=PipSession())])

