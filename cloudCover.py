# import libraries

"""import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from netCDF4 import Dataset
import rasterio.plot
import rasterio
import pyproj
import nasa_hls as hls
import fmask
from createGeoTiffFromHLS import create_multiband_geotif
"""

import gdal
#from s2cloudless import S2PixelCloudDetector, CloudMaskRequest
import numpy as np
import os
import matplotlib.pyplot as plt
# import cv2
from osgeo import gdal_array

import utils

directoryPath = "/home/Usuario/Documents/SatelliteImages"

filePathArray = []
clearSkyImges = [0, 0, 0]
clearSkyImgesPaths = []
fiftyPercentClouds = [0, 0, 0]


def createlistoffiles():
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath):
            for year in os.listdir(tilePath):
                yearPath = os.path.join(tilePath, year)
                if os.path.isdir(yearPath):
                    for hlsDirectory in os.listdir(yearPath):
                        dirPath = os.path.join(yearPath, hlsDirectory)
                        if os.path.isdir(dirPath) and hlsDirectory == "S30":
                            for file in os.listdir(dirPath):
                                if file.endswith('.hdf'):
                                    filePath = os.path.join(dirPath, file)
                                    filePathArray.append(filePath)

def clear_sky(path):
    cloud_coverage = utils.extract_cloud_coverage(path)
    if cloud_coverage is None:
        return
    if cloud_coverage == 0:  # no clouds calculated for image
        if path.find("2016") != -1:  # path has 2016 in it
            clearSkyImges[0] = clearSkyImges[0] + 1
            clearSkyImgesPaths.append(path)
        if path.find("2017") != -1:
            clearSkyImges[1] = clearSkyImges[1] + 1
            clearSkyImgesPaths.append(path)
        if path.find("2018") != -1:
            clearSkyImges[2] = clearSkyImges[2] + 1
            clearSkyImgesPaths.append(path)
    if cloud_coverage < 26:  # 25% or less cloud coverage calculated
        if path.find("2016") != -1:
            fiftyPercentClouds[0] = fiftyPercentClouds[0] + 1
        if path.find("2017") != -1:
            fiftyPercentClouds[1] = fiftyPercentClouds[1] + 1
        if path.find("2018") != -1:
            fiftyPercentClouds[2] = fiftyPercentClouds[2] + 1


def create_bandarray(path):
    hdf_dataset = gdal.Open(path)
    subdatasets = hdf_dataset.GetSubDatasets()
    print(subdatasets)
    wms_bands = []
    for entry in subdatasets:
        if entry[0].find("B01") != - 1 or entry[0].find("band01") != - 1:
            dataset = gdal.Open(entry[0])
            buffer_obj = dataset.ReadAsArray()
    # get required bands as arays
    for entry in subdatasets:
        if (entry[0].find("B01") != -1 or entry[0].find("B02") != -1 or entry[0].find(
                "B04") != -1 or entry[0].find("B05") != -1 or entry[0].find("B8A") != -1 or entry[0].find(
            "B08") != -1 or entry[0].find("B09") != -1 or entry[0].find("B10") != -1 or entry[0].find("B11") != -1 or
            entry[0].find(
                "B12") != -1) or (entry[0].find("band01") != -1 or entry[0].find("band02") != -1 or entry[0].find(
            "band04") != -1 or entry[0].find("band05") != -1 or entry[0].find("band06") != -1 or entry[0].find(
            "band07") != -1 or entry[0].find("band09") != -1 or entry[0].find("band10") != -1 or entry[0].find(
            "band11") != -1 or
                                  entry[0].find(
                                      "band03") != -1):  # and entry[0].endswith(".jp2")
            dataset = gdal.Open(entry[0])
            print(dataset)
            wms_bands.append(dataset.ReadAsArray(buf_obj=buffer_obj))
    return wms_bands


# create_geotif("/home/Usuario/Documents/SatelliteImages/21LYH/2017/S30/HLS.S30.T21LYH.2017202.v1.4.hdf", 1)
# print(clearSkyImges)
# print(fiftyPercentClouds)
def example_cloudmask():
    layerPath = "/home/Usuario/Documents/sentinelHub/S2A_MSIL1C_20190904T140051_N0208_R067_T21LWH_20190904T172119.SAFE/GRANULE/L1C_T21LWH_A021943_20190904T140439/IMG_DATA"
    wms_bands = []
    # set resolution based on specific band, res: B01:60,B02:10:B05:20
    for file in os.listdir(layerPath):
        if (file.find("B01") != -1):
            dataset = gdal.Open(os.path.join(layerPath, file))
            bufer_obj = dataset.ReadAsArray()
    # get required bands as arays
    for file in os.listdir(layerPath):
        if (file.find("B01") != -1 or file.find("B02") != -1 or file.find(
                "B04") != -1 or file.find("B05") != -1 or file.find("B8A") != -1 or file.find(
            "B08") != -1 or file.find("B09") != -1 or file.find("B10") != -1 or file.find("B11") != -1 or file.find(
            "B12") != -1 and file.endswith(".jp2")):
            dataset = gdal.Open(os.path.join(layerPath, file))
            wms_bands.append(dataset.ReadAsArray(buf_obj=bufer_obj))
    return wms_bands
    """template_file = "/home/Usuario/Documents/S2A_MSIL1C_20190914T140051_N0208_R067_T21LYH_20190914T153817.SAFE/GRANULE/L1C_T21LYH_A022086_20190914T140051/IMG_DATA/T21LYH_20190914T140051_B01.jp2"
    out_prob = "/home/Usuario/Documents/S2A_MSIL1C_20190914T140051_N0208_R067_T21LYH_20190914T153817.SAFE/GRANULE/L1C_T21LYH_A022086_20190914T140051/IMG_DATA/out_prob.tif"
    out_mask = "/home/Usuario/Documents/S2A_MSIL1C_20190914T140051_N0208_R067_T21LYH_20190914T153817.SAFE/GRANULE/L1C_T21LYH_A022086_20190914T140051/IMG_DATA/out_mask.tif"""""

'''
band_array: area with all bands created by create_bandarray
path = 
'''
def createCloudMask(band_array, path):
    stacked = np.stack(band_array, -1)
    # print(stacked / 10000)
    # swapped = np.moveaxis(stacked, 0, 2)  # shape (y_pixels, x_pixels, n_bands)

    arr4d = np.expand_dims(stacked / 10000,
                           0)  # shape (1, y_pixels, x_pixels, n_bands) # s2cloudless requires binary map
    cloud_detector = S2PixelCloudDetector(threshold=0.7, average_over=4, dilation_size=2)
    cloud_prob_map = cloud_detector.get_cloud_probability_maps(np.array(arr4d))
    cloud_masks = cloud_detector.get_cloud_masks(np.array(arr4d))
    # show files
    plt.figure(figsize=(50, 50))
    plt.imshow(np.squeeze(cloud_masks))  # check whz process not stopping, when closing
    plt.show()
    # save files

    template_file = "/home/Usuario/Documents/sentinelHub/S2A_MSIL1C_20190904T140051_N0208_R067_T21LWH_20190904T172119.SAFE/GRANULE/L1C_T21LWH_A021943_20190904T140439/IMG_DATA/T21LWH_20190904T140051_B01.jp2"
    print(template_file)
    out_prob = path[:-31] + "out_prob.tif"
    out_mask = path[:-31] + "out_mask.tif"
    output = gdal_array.SaveArray(cloud_prob_map[0, :, :], out_prob, format="GTiff", prototype=template_file)
    output = None
    output = gdal_array.SaveArray(cloud_masks[0, :, :], out_mask, format="GTiff", prototype=template_file)
    output = None


if __name__ == '__main__':
    # createlistoffiles()
    band_array = example_cloudmask()
    createCloudMask(band_array,
                    "/home/Usuario/Documents/sentinelHub/S2A_MSIL1C_20190904T140051_N0208_R067_T21LWH_20190904T172119.SAFE/GRANULE/L1C_T21LWH_A021943_20190904T140439/IMG_DATA")
    """
    for hlspath in filePathArray:
        if hlspath.find('21LYH') != -1:
            print("Working with file: " + hlspath)
            path = hlspath
            band_array = create_bandarray(hlspath)
            createCloudMask(band_array, hlspath)
            break
            hls_metadata = gdal.Info(path)
         hdf_dataset = gdal.Open(path)
         subdatasets = hdf_dataset.GetSubDatasets()
         qa_metadata = gdal.Info(subdatasets[10][0])
         cc = extract_cloud_coverage(hls_metadata)

   ''' hlspath = "/home/Usuario/Documents/SatelliteImages/21LWH/2016/S30/HLS.S30.T21LWH.2016013.v1.4.hdf"
    band_array = create_bandarray(hlspath)
    print(band_array)"""

# clear_sky(path) #to calculate amount of images with certain cloud coverage
# create_multiband_geotif(path)

# create FMask for files with fmask pyhton library
