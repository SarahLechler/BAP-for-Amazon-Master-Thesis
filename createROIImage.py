# Import Python 3 print function
from __future__ import print_function
# Import OGR -
from osgeo import ogr
import gdal
import numpy as np

"""
creates polygons from training data point layer
inout:  index name String (NDVI, RNSDI, SAVI, GEMI EVI)
        path String path to training data
        year: year of training data

"""


def createROIImage(path, year, tile):
    print(f"creating ROI images for {year} for the tile {tile}")
    ds_path = f"{path}/template_file_{tile}.tif"
    print(ds_path)
    raster_ds = gdal.Open(ds_path,
                          gdal.GA_ReadOnly)  # take template image "(../../../../)scratch/tmp/s_lech05/hls_data/{tile}/template_file_{tile}.tif"

    # Fetch projection and extent
    proj = raster_ds.GetProjectionRef()
    ext = raster_ds.GetGeoTransform()
    ds_data_path = f'trainingData/{tile}{year}_trainingData.shp'
    source_ds = ogr.Open(ds_data_path)
    source_layer = source_ds.GetLayer()
    spatialRef = source_layer.GetSpatialRef()

    # 2) Creating the destination raster data source

    target_ds = gdal.GetDriverByName('GTiff').Create(
        path + 'training_data_roi'+year+'.tif', 3660, 3660, 1,
        gdal.GDT_UInt16)

    target_ds.SetGeoTransform(ext)
    target_ds.SetProjection(proj)

    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(-9999)

    status = gdal.RasterizeLayer(target_ds, [1], source_layer,
                                 options=['ALL_TOUCHED=TRUE',  # rasterize all pixels touched by polygons
                                          'ATTRIBUTE=id'])  ## put in the attribute that contains the label
    # out_img, out_transform = mask(status, shapes=bbox, crop=True) #How to cut the rasterlayer?

    target_ds = None
    if status != 0:
        print("Could not create ROI file")
    else:
        print("Success")

    roi_ds = gdal.Open(path + 'training_data_roi'+year+'.tif', gdal.GA_ReadOnly)
    roi = roi_ds.GetRasterBand(1).ReadAsArray()

    # How many pixels are in each class?
    classes = np.unique(roi)
    classes = classes
    # Iterate over all class labels in the ROI image, printing out some information
    for c in classes:
        print('for tile ' + tile + 'and year ' + year + 'Class {c} contains {n} pixels'.format(c=c,
                                                     n=(roi == c).sum()))
