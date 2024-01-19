from osgeo import gdal
import rasterio
import os

class Raster(object):
    """
    A class to represent a raster object.
    
    """
    
    def __init__(self, source, iteration=None, timestep=None):
        self.__source = source
        self.__name = self.__init_name(iteration, timestep)
        self.__dimensions = self.__init_dimensions()
        self.__extent = self.__init_extent()
        self.__resolution = self.__init_resolution()
        self.__crs = self.__init_crs()
        
    def __str__(self):
        
        return self.__to_string()
    
    def __repr__(self):
        
        return self.__to_string()
    
    def __to_string(self):
        
        s = "class: Raster\n"
        s += "source: %s\n" % self.source
        s += "name: %s\n" % self.name
        s += "dimensions: %s\n" % self.dimensions
        s += "resolution: %s\n" % self.resolution
        s += "extent: %s\n" % self.extent
        s += "crs: %s\n" % self.crs
        
        return s
        
    @property
    def source(self):
        """Gets the filepath of the raster"""
        return self.__source
    
    @property
    def name(self):
        """Gets the name of the raster"""
        return self.__name
    
    @property
    def dimensions(self):
        """Gets the dimensions of the raster"""
        return self.__dimensions
    
    @property
    def resolution(self):
        """Gets the resolution of the raster"""
        return self.__resolution
    
    @property
    def extent(self):
        """Gets the extent of the raster"""
        return self.__extent
    
    @property
    def crs(self):
        """Gets the coordinate system of the raster"""
        return self.__crs
    
    def values(self, band=None):
        """
        Gets the values in each cell of the raster
        

        Parameters
        ----------
        band : Int, optional
            The specific band to return. If None, then all bands in the raster
            are returned in the array, with the first dimension of the array
            corresponding to the band number. The default is None.

        Returns
        -------
        values : numpy array
            Array of values corresponding to the cell values in the raster.

        """
        
        if band is None:
            with rasterio.open(self.source) as raster:
                values = raster.read()
                if values.shape[0] == 1:
                    values = values[0]
            return values
        
        else:
            with rasterio.open(self.source) as raster:
                values = raster.read(band)
            return values
        
    def __init_name(self, iteration, timestep):
        
        prefix = os.path.splitext(os.path.basename(self.source))[0]
        
        if prefix.endswith(f".it{iteration}.ts{timestep}"):
            return prefix
        else:
            return prefix + ".it" + str(iteration) + ".ts" + str(timestep)
    
    def __init_dimensions(self):
        
        dim_dict = {"height": [], "width": [], "cells": []}
        
        with rasterio.open(self.source) as raster:
            
            dim_dict["height"].append(raster.height)
            dim_dict["width"].append(raster.width)
            dim_dict["cells"].append(raster.height * raster.width)
        
        return dim_dict
    
    def __init_extent(self):
        
        extent_dict = {"xmin" : [], "xmax": [], "ymin": [], "ymax": []}
        
        with rasterio.open(self.source) as raster:
            
            extent_dict["xmin"].append(raster.bounds[0])
            extent_dict["xmax"].append(raster.bounds[2])
            extent_dict["ymin"].append(raster.bounds[1])
            extent_dict["ymax"].append(raster.bounds[3])
            
        return extent_dict
    
    def __init_resolution(self):
        
        x_num = self.dimensions["width"][0]
        y_num = self.dimensions["height"][0]
        
        x_range = self.extent["xmax"][0] - self.extent["ymin"][0]
        y_range = self.extent["ymax"][0] - self.extent["ymin"][0]
        
        x_res = x_range / x_num
        y_res = y_range / y_num
        
        res_dict = {"x": x_res, "y": y_res}
        
        return res_dict
    
    def __init_crs(self):
        
        with rasterio.open(self.source) as raster:
            
            crs = raster.crs
            
        return crs
    
        

