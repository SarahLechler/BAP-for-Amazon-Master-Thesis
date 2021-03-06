from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import cohen_kappa_score

import gdal
from osgeo.gdalconst import *
import ogr
import os
import numpy as np
import multiprocessing as mp
import pandas as pd
import sys


def create_prodes_layer(path, prodes_path_shp, tile):
    '''
    creates Raster Prodes Layer
    Input:
    path: String path to template file
    prodes_path_shp: String path to prodes shapefile
    tile: String name of tile
    Output:
    prodes:Array with prodes data
    '''

    # First we will open our raster image, to understand how we will want to rasterize our vector
    ds_path = f"{path}/template_file_{tile}.tif"
    raster_ds = gdal.Open(ds_path, gdal.GA_ReadOnly)

    # Fetch projection and extent
    proj = raster_ds.GetProjectionRef()
    ext = raster_ds.GetGeoTransform()
    prodes_path = prodes_path_shp
    shp_driver = ogr.GetDriverByName("ESRI Shapefile")
    source_ds = shp_driver.Open(prodes_path, 0)
    layer = source_ds.GetLayer()
    source_layer = source_ds.GetLayer()

    # 2) Creating the destination raster data source

    target_ds = gdal.GetDriverByName('GTiff').Create(
        prodes_path_shp[-3]+'tif', 3660, 3660, 1,
        gdal.GDT_Float32)  ##COMMENT 2 f'validationData/{tile}_prodes.tif'

    target_ds.SetGeoTransform(ext)  # COMMENT 3
    target_ds.SetProjection(proj)

    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(-9999)  ##COMMENT 5

    status = gdal.RasterizeLayer(target_ds, [1], source_layer,
                                 options=['ALL_TOUCHED=TRUE',  # rasterize all pixels touched by polygons
                                          'ATTRIBUTE=ORIGIN_ID'])  ##COMMENT 6
    # out_img, out_transform = mask(status, shapes=bbox, crop=True) #How to cut the rasterlayer?

    target_ds = None  ##COMMENT 7

    if status != 0:
        print("I don't think it worked...")
    else:
        print("Success")

    prodes_ds = gdal.Open(prodes_path_shp[-3]+'tif', gdal.GA_ReadOnly) #f'validationData/{tile}_prodes.tif'
    prodes = prodes_ds.GetRasterBand(1).ReadAsArray()
    prodes = np.where(prodes != -9999, 1, 255).astype(np.float).ravel()
    print(f"amount of deforestation pixel in prodes: {np.unique(prodes, return_counts='true')}")
    return prodes #prodes:Array with prodes data


def extract_extent(index):
    metadata = get_bfastlayer(index)[0]
    cc_index = metadata.find("Upper Left")
    if cc_index != -1:
        upper_left = metadata[cc_index + 15:cc_index + 38]
    cc_index = metadata.find("Lower Left")
    if cc_index != -1:
        lower_left = metadata[cc_index + 15:cc_index + 38]
    cc_index = metadata.find("Upper Right")
    if cc_index != -1:
        upper_right = metadata[cc_index + 15:cc_index + 38]
    cc_index = metadata.find("Lower Right")
    if cc_index != -1:
        lower_right = metadata[cc_index + 15:cc_index + 38]

    wkt = f"POLYGON (({upper_left.split(',')[0]} {upper_left.split(',')[1]},{lower_left.split(',')[0]} {lower_left.split(',')[1]}," \
          f"{upper_right.split(',')[0]} {upper_right.split(',')[1]},{lower_right.split(',')[0]} {lower_right.split(',')[1]},{upper_left.split(',')[0]} {upper_left.split(',')[1]}))"
    return wkt


def get_bfastlayer(tile, index, bap):
    '''
    fetches BFast layer as array
    Input:
    tile: String Name of tile
    index: String Name of index
    bap: Boolean if fetches for BAP images
    Output:
    bfast_md:metadata of bfast layer and bfast_array:Array with bfast breaks
    '''
    if bap:
        bfast_path = f"../Ergebnisse_BFAST/{index}{tile}_breaks_2019_BAP_bfast.tif"
    else:
        bfast_path = f"../Ergebnisse_BFAST/{index}{tile}_breaks_2019_bfast.tif"
    print(f"working with file: {bfast_path}")
    bfast_md = gdal.Info(bfast_path)
    dataset = gdal.Open(bfast_path)
    bfast_array = dataset.ReadAsArray()
    bfast_array = np.where(bfast_array != -1, 1, 255).astype(np.float)
    rows = dataset.RasterYSize
    cols = dataset.RasterXSize

    # create the output image
    driver = dataset.GetDriver()
    # print driver
    outDs = driver.Create(f'{tile}{index}_breaks_2019_bfast_tifArray', cols, rows, 1, GDT_Int32)
    if outDs is None:
        print
        'Could not create reclass_40.tif'
        sys.exit(1)

    outBand = outDs.GetRasterBand(1)

    # write the data
    outBand.WriteArray(bfast_array, 0, 0)

    # flush data to disk, set the NoData value and calculate stats
    outBand.FlushCache()
    outBand.SetNoDataValue(-99)

    # georeference the image and set the projection
    outDs.SetGeoTransform(dataset.GetGeoTransform())
    outDs.SetProjection(dataset.GetProjection())
    bfast_array = bfast_array.ravel()

    return bfast_md, bfast_array # metadata of bfast layer and Array with bfast breaks


def get_RFlayer(tile, index, bap):
    '''
    fetches Random Forest layer as array
    Input:
    tile: String Name of tile
    index: String Name of index
    bap: Boolean if fetches for BAP images
    Output:
    rf_md:metadata of rf layer and rf_array:Array with rf classification
    '''
    if bap:
        rf_path = f"../ErgebnisseRF/{tile}/classified_{index}2019.gtif"
    else:
        rf_path = f"../ErgebnisseRF/{tile}/classified_Months{index}2019.gtif"
    print(f"working with file: {rf_path}")
    rf_md = gdal.Info(rf_path)
    dataset = gdal.Open(rf_path)
    rf_array = dataset.ReadAsArray()
    rf_array = np.where(rf_array == 4, 1, 255).astype(np.float)

    # read in the crop data and get info about it
    rows = dataset.RasterYSize
    cols = dataset.RasterXSize

    # create the output image
    driver = dataset.GetDriver()
    # print driver
    outDs = driver.Create(f'{tile}{index}_2019_rf_tifArray', cols, rows, 1, GDT_Int32)
    if outDs is None:
        print('Could not create reclass_40.tif')
        sys.exit(1)

    outBand = outDs.GetRasterBand(1)

    # write the data
    outBand.WriteArray(rf_array, 0, 0)

    # flush data to disk, set the NoData value and calculate stats
    outBand.FlushCache()
    outBand.SetNoDataValue(-99)

    # georeference the image and set the projection
    outDs.SetGeoTransform(dataset.GetGeoTransform())
    outDs.SetProjection(dataset.GetProjection())

    rf_array = rf_array.ravel()
    return rf_md, rf_array # rf_md:metadata of rf layer and rf_array:Array with rf classification


def calc_accuracy_bfast(input):
    '''
    runs statistical calculations for the BFAST layer
    Input:
    input: Array[] with index, prodes_layer_aray, tilename, bap
    Output:
    prints calculated statistics
    '''
    bfast_layer = get_bfastlayer(input[2], input[0], input[3])[1]
    score = accuracy_score(input[1], bfast_layer)
    p_score = precision_score(input[1], bfast_layer, average=None)
    binary_score = f1_score(input[1], bfast_layer, average=None)
    cm = confusion_matrix(input[1], bfast_layer)
    # Now the normalize the diagonal entries
    man_accuracy = compare(input[1], bfast_layer)
    kappa_score = cohen_kappa_score(input[1], bfast_layer)
    data = {'y_Actual': input[1],
            'y_Predicted': bfast_layer
            }

    df = pd.DataFrame(data, columns=['y_Actual', 'y_Predicted'])

    pd_matrix = pd.crosstab(df['y_Actual'], df['y_Predicted'], rownames=['Actual'], colnames=['Predicted'],
                            margins=True)
    print(f"Using BFAST monitor with index: {input[0]}, the pd matrix is:\n {pd_matrix}")
    print(f"Using BFAST monitor with index: {input[0]}, the kappa score is:\n {kappa_score}")

    print(f"Using BFAST monitor with index: {input[0]}, the accuracy is: {score}")
    print(f"Using BFAST monitor with index: {input[0]}, the precision is: {p_score}")
    print(f"Using BFAST monitor with index: {input[0]}, the binary accuracy is: {binary_score}")
    print(f"Using BFAST monitor with index: {input[0]}, the normalized confusion matrix is:\n {cm}")
    print(
        f"Using BFAST monitor with index: {input[0]}, the maually calculated accuracy is: {man_accuracy}")


def calc_accuracy_rf(input):
    '''
    runs statistical calculations for the RF layer
    Input:
    input: Array[] with index, prodes_layer_aray, tilename, bap
    Output:
    prints calculated statistics
    '''
    rf_layer = get_RFlayer(input[2], input[0], input[3])[1]
    score = accuracy_score(input[1], rf_layer)
    p_score = precision_score(input[1], rf_layer, average=None)
    binary_score = f1_score(input[1], rf_layer, average=None)
    cm = confusion_matrix(input[1], rf_layer)
    kappa_score = cohen_kappa_score(input[1], rf_layer)

    data = {'y_Actual': input[1],
            'y_Predicted': rf_layer
            }

    df = pd.DataFrame(data, columns=['y_Actual', 'y_Predicted'])

    pd_matrix = pd.crosstab(df['y_Actual'], df['y_Predicted'], rownames=['Actual'], colnames=['Predicted'],
                            margins=True)

    print(f"Using RF with index: {input[0]} for the tile {input[2]}, the pd matrix is:\n {pd_matrix}")
    print(f"Using RF with index: {input[0]} for the tile {input[2]}, the kappa score is:\n {kappa_score}")

    print(f"Using RF with index: {input[0]} for the tile {input[2]}, the accuracy is: {score}")
    print(f"Using RF monitor with index: {input[0]} for the tile {input[2]}, the precision is: {p_score}")
    print(f"Using RF monitor with index: {input[0]} for the tile {input[2]}, the binary accuracy is: {binary_score}")
    print(
        f"Using RF monitor with index: {input[0]} for the tile {input[2]}, the normalized confusion matrix is:\n {cm}")
    """print(f"Using RF monitor with index: {input[0]}, the maually calculated accuracy is: {man_accuracy}")"""


def compare(prodes, classification):
    '''
    runs manual accuracy calulations for classification layer
    Input:
    prodes: Array[] prodes_layer array
    classification: Array[] classification_layer array
    Output:
    returns calulated accuracy
    '''
    print("start comparing")
    totalPix = len(prodes)
    rightClassDeforest = 0
    rightClassNoData = 0
    falsePos = 0
    falseNeg = 0
    for i in range(len(prodes)):
        if (prodes[i] == classification[i] and prodes[i] == 1):
            rightClassDeforest = rightClassDeforest + 1
        elif (prodes[i] == classification[i] and prodes[i] == 255):
            rightClassNoData = rightClassNoData + 1
    accuracy = (rightClassDeforest + rightClassNoData) / totalPix

    return accuracy


if __name__ == "__main__":
    '''
    runs statistrical calculations for the BFAST layer and the Random Forest Layer
    '''
    tile = "21LYH"
    path = f"../hls_dataset/BAPs/{tile}/"
    prodes_path = f'validationData/{tile}_prodes2019.shp'
    bap = False
    prodes_layer = create_prodes_layer(path, tile, prodes_path)
    index_array = [["NDVI", prodes_layer, tile, bap], ["NDMI", prodes_layer, tile, bap],
                   ["SAVI", prodes_layer, tile, bap],
                   ["EVI", prodes_layer, tile, bap]]
    # accuracy Bfast
    pool = mp.Pool(2)
    resultBFAST = pool.imap(calc_accuracy_bfast, index_array)
    resultBFAST = None
    pool.close()
    pool.join()
    # accuracy RF
    pool = mp.Pool(2)
    resultRF = pool.imap(calc_accuracy_rf, index_array)

    pool.close()
    pool.join()
    resultRF = None
