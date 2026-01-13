# Copyright (c) 2025 Apex Resource Management Solution Ltd. (ApexRMS). All rights reserved.
# MIT License

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version without importing the package
version = {}
exec((this_directory / "pysyncrosim" / "_version.py").read_text(encoding="utf-8"), version)
__version__ = version["__version__"]

setup(
    name="pysyncrosim",
    version=__version__,
    description="Python interface to SyncroSim",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ApexRMS",
    author_email="info@apexrms.com",
    url="https://syncrosim.com/",
    packages=find_packages(exclude=("tests",)),
    install_requires=["numpy", "pandas", "rasterio"],
    extras_require={
        "dev": ["pytest", "build", "twine"],
    },
)
