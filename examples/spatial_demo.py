# =============================================================================
# # Set up environment
# =============================================================================

# Import packages

import pandas as pd
import os
import pysyncrosim as ps
import rasterio
from matplotlib import pyplot

# Load Session
mySession = ps.Session()

# Check SyncroSim version
mySession.version()

# Check which packages are installed
mySession.packages()

# Install helloworldSpatial package
mySession.add_packages("helloworldSpatial")

# Make sure it was installed
mySession.packages()

# Update installed packages
mySession.update_packages("myPackage")

# Remove installed packages
mySession.remove_packages("myPackage")

# =============================================================================
# # Create a modeling workflow
# =============================================================================

# Create a new Library using the helloworldSpatial package
myLibrary = ps.library(name = "spatialDemo",
                       session = mySession, 
                       package = "helloworldSpatial",
                       overwrite = True)

# You can also open an existing Library using the same function
myLibrary = ps.library(name = "spatialDemo",
                       session = mySession,
                       package = "helloworldSpatial")

# Retrieve information about the Library instance attributes
myLibrary.info

# Create (or open) a Project in this Library
myProject = myLibrary.projects(name = "Definitions")

# When creating a new Scenario, uses "Definitions" Project by default
myScenario = myLibrary.scenarios(name = "Spatial Scenario")

# Could also create / open a new Scenario using a Project class instance
myScenario = myProject.scenarios(name = "Spatial Scenario")

# =============================================================================
# # Modify Datasheets
# =============================================================================

# List Datasheets for this Scenario
myScenario.datasheets()

# Modify RunControl
myScenario.datasheets(name = "helloworldSpatial_RunControl")

runControlDataFrame = pd.DataFrame({"MinimumIteration": [1],
                                    "MaximumIteration": [5],
                                    "MinimumTimestep": [1],
                                    "MaximumTimestep": [10]})

myScenario.save_datasheet(name = "helloworldSpatial_RunControl",
                          data = runControlDataFrame)

myScenario.datasheets(name = "helloworldSpatial_RunControl")

# Modify InputDatasheet
myScenario.datasheets(name = "helloworldSpatial_InputDatasheet")

InputDataFrame = pd.DataFrame({"mMean": [2],
                               "mSD": [4],
                               "InterceptRasterFile": [
                                   os.getcwd()+".\input-raster.tif"]})

myScenario.save_datasheet(name = "helloworldSpatial_InputDatasheet",
                          data = InputDataFrame)

myScenario.datasheets(name = "helloworldSpatial_InputDatasheet")

# Modify Pipeline Datasheet
myScenario.datasheets(name = "core_Pipeline")
pipelineDataFrame1 = myScenario.datasheets(name = "core_Pipeline")

pipelineDataFrame2 = pd.DataFrame({"StageNameID": ["First Model",
                                                   "Second Model"],
                                   "RunOrder": [1, 2]})
pipelineDataFrame1 = pd.concat([pipelineDataFrame1, pipelineDataFrame2])

myScenario.save_datasheet(name = "core_Pipeline", data = pipelineDataFrame1)

myScenario.datasheets(name = "core_Pipeline")

# Copy the Scenario with all its Datasheets
myCopiedScenario = myScenario.copy(name = "My Copied Scenario")

# =============================================================================
# # Run Scenarios
# =============================================================================

# Run using a Scenario method
myResultsScenario = myScenario.run(jobs=2)

# Run using Library method
myResultsScenario = myLibrary.run(scenarios=myScenario, jobs=5)

# Run multiple Scenarios at once (can use Scenario instances, names, or IDs)
myResultsScenarioAll = myLibrary.run(scenarios=[myScenario,
                                                myCopiedScenario],
                                     jobs=5)

# =============================================================================
# # View results
# =============================================================================

# Check Results Scenario attributes
myResultsScenario.info

# Check if Scenario is a Results Scenario
myResultsScenario.is_result

# Check the parent ID of a Results Scenario
myResultsScenario.parent_id

# Check which Results Scenarios belong to a parent Scenario
myScenario.results()
myCopiedScenario.results()

# Retrieve a specific results Scenario using its ID
myResultsScenario = myScenario.results(sid=3)

# Check the run log
myResultsScenario.run_log()

# View Results Scenario Datasheets
myResultsScenario.datasheets(name = "IntermediateDatasheet").head()
myResultsScenario.datasheets(name = "OutputDatasheet").head()

# =============================================================================
# # View spatial results
# =============================================================================

# Get a raster 
spatialRaster = myResultsScenario.datasheet_rasters(
    datasheet = "IntermediateDatasheet",
    column = "OutputRasterFile",
    iteration = 3,
    timestep = 4)

# View the raster metadata
spatialRaster

# View cell values and plot raster using the Raster class instance
## use the raster object
spatialRaster.values()
pyplot.imshow(spatialRaster.values())

# You can also specify the band you want to extract
spatialRaster.values(band=1)

# You can further modify the source TIF using rasterio
with rasterio.open(spatialRaster.source) as raster:
    cell_values = raster.read()
cell_values

with rasterio.open(spatialRaster[0].source) as raster:
    rasterio.plot.show(raster)

# Get multiple rasters in a list
spatialRasters = myResultsScenario.datasheet_rasters(
    datasheet = "helloworldSpatial_IntermediateDatasheet",
    column = "OutputRasterFile")

spatialRasters[15]

pyplot.imshow(spatialRasters[15].values(), cmap = "pink")
pyplot.show()
