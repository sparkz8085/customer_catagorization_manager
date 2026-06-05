from pathlib import Path

from setuptools import find_packages, setup


def read_requirements():
    requirements_path = Path(__file__).with_name("requirements.txt")
    return [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="src",
    version="0.0.1",
    author="iNeuron",
    author_email="cloud@ineuron.ai",
    packages=find_packages(),
    install_requires=read_requirements(),
)
