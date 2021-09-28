# Copyright (c) 2021 Apex Resource Management Solution Ltd. (ApexRMS). All rights reserved.
# MIT License

from setuptools import setup, find_packages

setup(name="pysyncrosim",
      version="1.0.0",
      description="Python interface to SyncroSim",
      author="ApexRMS",
      author_email="info@apexrms.com",
      url="www.apexrms.com",
      packages=find_packages(exclude="tests"),
      install_requires=["pandas", "numpy", "rasterio"])

