# Copyright (c) 2025 Apex Resource Management Solution Ltd. (ApexRMS). All rights reserved.
# MIT License

from setuptools import setup, find_packages
from pathlib import Path
from pysyncrosim._version import __version__

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name="pysyncrosim",
      version=__version__,
      description="Python interface to SyncroSim",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="ApexRMS",
      author_email="info@apexrms.com",
      url="https://syncrosim.com/",
      packages=find_packages(exclude="tests"))

install_requires=['numpy', 'pandas', 'rasterio']

extras_require=['numpy', 'pandas', 'rasterio']