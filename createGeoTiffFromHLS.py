from osgeo import gdal, ogr
import os

"""
ceates single band GeoTif from the given dataset
input: dataset: path to dataset
"""


def create_singleband_geotif(dataset, path):
    gdal.Translate(path[:-4] + "/" + dataset[-3:]+'_output_file.tif', dataset, options=[("-of"), ("GTiff")])


"""
    creates multi band GeoTif 
    input: path: hdf file path
"""

"""def create_singleband_geotif(path, band):
    hdf_dataset = gdal.Open(path)
    subdatasets = hdf_dataset.GetSubDatasets()
    gdal.Translate(path + '_output_file.tif', subdatasets[band - 1][0], options=[("-of"), ("GTiff")])
    hdf_dataset = None"""

def create_multiband_geotif(path):
    hdf_dataset = gdal.Open(path)
    subdatasets = hdf_dataset.GetSubDatasets()
    if not (os.path.isdir(path[:-4])):
        os.mkdir(path[:-4])
    for dataset in subdatasets:
        create_singleband_geotif(dataset[0], path)
