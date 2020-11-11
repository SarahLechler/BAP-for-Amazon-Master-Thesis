"""
This code aims to pre-process hls-datasets (specifically the tiles 21LYH anf 21LYG from 2013-2020),
to create Best-Available-Pixel composites and to run BFAST and Random Forest with the preprocessed images to detect deforestation
 The images are stored in a folder called /scratch/tmp/s_lech05/hls_data/*tile*/*name*method*
"""

from osgeo import gdal_array
import multiprocessing as mp
import os
from functools import partial

import hlsCloudMask
import createGeoTiffFromHLS
import createClearSkyImg
import calculateIndices
import ranking
import create_time_series
import createMonthlyPatchedImage
import runBFAST
# import convertToHDF5
# import RandomForest.runDecisionTree as rundt
import runKMeans as km
import create_yearly_time_series as yts
import createInputData as cd
import runRandomForest as rf
import createROIImage as roi

def save_results_to_tif(bfast_array, method, name):
    '''
    Saves BFAST results to a .tif file
    Input:
    bfast_array: Array [] with BFAST classifications
    method: String "" If Monhtly Images or BAP Images were used and breaks or mean
    name: String "" Name of the Index and tile
    '''
    if name.find('LYH') != -1:
        template_file = '/scratch/tmp/s_lech05/hls_data/21LYH/template_file_21LYH.tif'
        out_path = '/scratch/tmp/s_lech05/hls_data/21LYH/' + name + method + '_bfast.tif'
        output = gdal_array.SaveArray(bfast_array, out_path, format="GTiff", prototype=template_file)
        print("saved file to " + out_path)
        out_path = None
        output = None
        bfast_array = None
        template_file = None
    else:
        template_file = '/scratch/tmp/s_lech05/hls_data/21LYG/template_file_21LYG.tif'
        out_path = '/scratch/tmp/s_lech05/hls_data/21LYG/' + name + method + '_bfast.tif'
        output = gdal_array.SaveArray(bfast_array, out_path, format="GTiff", prototype=template_file)
        print("saved file to " + out_path)
        out_path = None
        output = None
        bfast_array = None
        template_file = None



def runCalcsBFAST(calc_array, bap):
    '''
    Runs BFAST calculations
    Input:
    calc_array: Array[] with the name of the index and the tile
    bap: Boolean If Monhtly Images or BAP Images should be used
    '''
    name = calc_array[0]
    tile = calc_array[1]
    print(f"running BFAST calcs for index {name} and tile {tile}")
    timeseries = create_time_series.create_time_series(name, tile, bap) #create timeseries for entire period
    results = runBFAST.run_bfast(timeseries) #run bfast with created timeseries and save it to results
    if bap:
        save_results_to_tif(results[0], "_breaks_2019_BAP", name + tile)
        save_results_to_tif(results[1], "_mean_2019_BAP", name + tile)
    else:
        save_results_to_tif(results[0], "_breaks_2019", name + tile)
        save_results_to_tif(results[1], "_mean_2019", name + tile)
    timeseries = None
    results = None

def runCalcsRF(inputarray, indice, path):
    '''
    Runs Random Forest calculations
    Input:
    inputarray: Array[] with the year and the tile
    indice: Array[] with indices names
    path: path to where the data is stored
    '''
    tile = inputarray[0]
    year = inputarray[1]
    main_path = path + tile + '/'
    roi.createROIImage(main_path, str(year), tile) #create reference image with training data
    for index in indice:
        print(f"starting RF fo {year} and {tile}")
        ts = yts.create_time_series(index, tile, year, True, path) #create timeseries for specific year
        data = cd.createData(ts, main_path, index, year) #create training data with timeseries and roi image
        km.runkmeans(data, year, index, tile)
        rf.runRF(index, main_path, year, data[0], data[1], ts, tile, True) #run random forest
        #rundt.runDT(data[0], data[1], index)
        ts = None

def createAllImages(path):
    '''
    Creates all Images
    Input:
    path: path to hdf file
    '''
    if "LYG" in path:
        tile = "21LYG"
    if "LYH" in path:
        tile = "21LYH"
    if not (os.path.isdir(path[:-3])):
        os.mkdir(path[:-3])
    # createGeoTiffFromHLS.create_multiband_geotif(path) #creates tifs for each band
    hlsCloudMask.create_cloudmask(path) #creates cloud mask for image from QA layer
    # clear_sky_path = createClearSkyImg.create_clear_sky_image(path) # masks out clouds for each band
    calculateIndices.calculate_indices_fromh5(path, tile) # calculates indices for image
    clear_sky_path = None
    print(f"finished creating Images for {path}")


def run_bap(tileAndYear):
    '''
    Creates all Images
    Input:
    tileAndYear: Array[] with tile and year
    '''
    tile = tileAndYear[0]
    year = tileAndYear[1]
    months = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]
    indices = ["NDMI", "SAVI", "EVI", "NDVI"]
    for month in months:
        createMonthlyPatchedImage.main(month, year, "/scratch/tmp/s_lech05/hls_data/", tile, indices,
                                       True) #creates composites afte calculating score for each image
    months = None
    indices = None
    tiles = None


if __name__ == '__main__':
    '''
    Runs all calculations
    '''
    img_paths = ranking.create_list_of_fileshdf5("/scratch/tmp/s_lech05/hls_data/") #create list of all available images

    # STEP 1: create images and cloudmask, mask out cloud and calculate indices in parallel
    print("starting Image Pool")
    pool = mp.Pool()
    result = pool.map(createAllImages, img_paths)
    pool.close()
    pool.join()
    
    # STEP 2: Run BAP method for given years and indices
    tilesAndYears = [["21LYG", 2013], ["21LYG", 2014], ["21LYG", 2015], ["21LYG", 2016], ["21LYG", 2017], ["21LYG", 2018],
                  ["21LYG", 2019], ["21LYG", 2020], ["21LYH", 2013], ["21LYH", 2014], ["21LYH", 2015], ["21LYH", 2016],
                  ["21LYH", 2017], ["21LYH", 2018], ["21LYH", 2019], ["21LYH", 2020]]
    #years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    pool = mp.Pool()
    result = pool.map(run_bap, tilesAndYears)
    pool.close()
    pool.join()

    # STEP 3: run BFAST algorithm in parallel
    # runCalcsBFAST(["NDVI", "21LYG"], True)

    print("starting bfast Pool for BAP images")
    img_array = [["SAVI", "21LYH"], ["EVI", "21LYH"], ["SAVI", "21LYG"], ["NDVI", "21LYG"],
                 ["EVI", "21LYG"], ["NDVI", "21LYH"], ["NDMI", "21LYG"], ["NDMI", "21LYH"]]
    pool = mp.Pool()
    result = pool.imap(partial(runCalcsBFAST, bap=True), img_array)

    pool.close()
    pool.join()
    result = None

    print("starting bfast Pool for monthly_images")
    img_array = [["SAVI", "21LYH"], ["EVI", "21LYH"], ["SAVI", "21LYG"], ["NDVI", "21LYG"],
                 ["EVI", "21LYG"], ["NDVI", "21LYH"], ["NDMI", "21LYG"], ["NDMI", "21LYH"]]
    pool = mp.Pool()
    result = pool.imap(partial(runCalcsBFAST, bap=False), img_array)

    pool.close()
    pool.join()
    result = None
    # for combi in img_array:
    #   runCalcsBFAST(combi, True)
    # STEP 4: run RF algorithm in parallel
    tilesAndYears = [["21LYG", 2014], ["21LYG", 2015], ["21LYG", 2016], ["21LYG", 2017],
                        ["21LYG", 2018],
                        ["21LYG", 2019], ["21LYH", 2014], ["21LYH", 2015],
                        ["21LYH", 2016],
                        ["21LYH", 2017], ["21LYH", 2018], ["21LYH", 2019]]


    indices = ["NDVI", "SAVI", "NDMI", "EVI"]
    tiles = ['21LYH', '21LYG']
    # years = [2019, 2018, 2017, 2016]
    # inputs = [indices, tiles, years]
    pool = mp.Pool()

    result = pool.map(partial(runCalcsRF, indice=indices, path="hls_dataset/BAPs/"),
                      tilesAndYears)  # " hls_dataset/BAPs/

    pool.close()
    pool.join()