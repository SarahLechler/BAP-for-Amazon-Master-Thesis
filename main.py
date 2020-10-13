"""
This code aims to pre-process hls-datasets (specifically the tiles 21LYH anf 21LYG from 2013-2017)
 and to run bfast with the prerocessed images to detect deforestation
 The images are stored in a folder called Images/*tile*/*year*/*(S30|L30)*
"""

from osgeo import gdal_array
import multiprocessing as mp
import os
import gdal
# hls download test
# from bs4 import BeautifulSoup
import collections
import datetime
import fnmatch
import numpy as np
import pandas as pd
#import rasterio
#import requests
#from subprocess import Popen, PIPE
# from tqdm import tqdm
#import urllib
#import warnings

import hlsCloudMask
import createGeoTiffFromHLS
import createClearSkyImg
import calculateIndices
import ranking
import create_time_series
import utils
import createMonthlyPatchedImage
# import runBFAST
import convertToHDF5


def save_results_to_tif(bfast_array, method, name):
    if name.find('LYH') != -1:
        template_file = '/data/sarah/pythonscripts/hls/Images/21LYH/2018/L30/HLS.L30.T21LYH.2018019.v1.4/d01_clear_sky.tif'
        out_path = '/data/sarah/pythonscripts/hls/Images/21LYH/' + name + method + '_bfast_tif'
        output = gdal_array.SaveArray(bfast_array, out_path, format="GTiff", prototype=template_file)
        output = None
    else:
        template_file = '/data/sarah/pythonscripts/hls/Images/21LYG/2016/L30/HLS.L30.T21LYG.2016110.v1.4/d01_clear_sky.tif'
        out_path = '/data/sarah/pythonscripts/hls/Images/21LYG/' + name + method + '_bfast_tif'
        output = gdal_array.SaveArray(bfast_array, out_path, format="GTiff", prototype=template_file)
        output = None


def runCalcs(calc_array):
    name = calc_array[0]
    tile = calc_array[1]
    print(f"running BFAST calcs for index {name} and tile {tile}")
    timeseries = create_time_series.create_time_series(name, tile, [3660, 3660])
    results = runBFAST.run_bfast(timeseries)
    save_results_to_tif(results[0], "_breaks_2018", name + tile)
    save_results_to_tif(results[1], "_mean_2018,", name + tile)


def createAllImages(path):
    print(path)
    if not (os.path.isdir(path[:-3])):
        os.mkdir(path[:-3])
    createGeoTiffFromHLS.create_multiband_geotif(path)
    hlsCloudMask.create_cloudmask(path)
    clear_sky_path = createClearSkyImg.create_clear_sky_image(path)
    calculateIndices.calculate_indices(clear_sky_path)





def run_bap(year):
    months = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]
    indices = ["SAVI", "EVI", "NDVI", "GEMI"]
    tiles = ["21LYG", "21LYH"]
    for month in months:
        for tile in tiles:
            createMonthlyPatchedImage.main(month, year, "../../../../scratch/tmp/s_lech05/hls_data", tile, indices)


if __name__ == '__main__':
    """
    img_paths = ranking.create_list_of_fileshdf5()
    # STEP 1: create images and cloudmask, mask out cloud and calculate indices in parallel
    print("starting Image Pool")
    pool = mp.Pool(2)
    result = pool.map(createAllImages, img_paths)
    pool.close()
    pool.join()
    """
    # STEP 2: Run BAP method for given years and indices
    years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    pool = mp.Pool(2)
    result = pool.map(run_bap, years)
    pool.close()
    pool.join()
     # STEP 2: run BFAST algorithm in parallel
    """print("starting bfast Pool")
    img_array = [["EVI", "21LYH"], ["EVI", "21LYG"],
                 ["SAVI", "21LYH"], ["SAVI", "21LYG"]]
    [["GEMI", "21LYH"],
                 ["GEMI", "21LYG"], ["EVI", "21LYH"], ["EVI", "21LYG"], ["NDVI", "21LYH"], ["NDVI", "21LYG"],
                 ["SAVI", "21LYH"], ["SAVI", "21LYG"]]
    pool = mp.Pool(2)
    result = pool.imap(runCalcs, img_array)

    pool.close()
    pool.join()"""
