# Copyright (c) 2021 Apex Resource Management Solution Ltd. (ApexRMS). All rights reserved.
# MIT License

from setuptools import setup, find_packages
from pysyncrosim._version import __version__

setup(name="pysyncrosim",
      version=__version__,
      description="Python interface to SyncroSim",
      author="ApexRMS",
      author_email="info@apexrms.com",
      url="https://www.apexrms.com",
      packages=find_packages(exclude="tests"))

install_requires=['numpy', 'pandas', 'rasterio']