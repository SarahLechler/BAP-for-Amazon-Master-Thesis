# getDate and distance to target date
# get aerosol quality
# get distance to cloud
# getsensor equality ?
testdataL30 = "hls_downloads/21LYH/2016/L30/HLS.L30.T21LYH.2016238.v1.4.h5"
testdataL30QA = "hls_downloads/21LYH/2016/L30/HLS.L30.T21LYH.2016238.v1.4/HLS.L30.T21LYH.2016238.v1.4.hdf_QA.tif"
testdataS30 = "hls_downloads/21LYH/2016/S30/HLS.S30.T21LYH.2016103.v1.4.h5"

import gdal
import os
import datetime
import numpy as np
import utils
import pandas as pd


# get aerosol quality
def get_qa_layer(path):
    '''
    Gets the path of the qa layer from a given path
    Input:
    path: String, path to layer
    Output:
    String,path to qa_layer
    '''
    folder_path = path[:-3]
    bands_list = os.listdir(folder_path)
    qa_path = ""
    for band in bands_list:
        if "_QA" in str(band):
            qa_path = os.path.join(folder_path, band)
    return qa_path


def get_aerosol_quality(pixel):
    '''
    Gets the value of the aerosol quality
    Input:
    pixel: Binary, 8-Bit binary pixel value
    Output:
    Integer, aersol value for given pixel
    '''
    """
    Aersol Quality: the 7&6 bit Number
    00 = Climatology
    01 = Low
    10 = Average
    11 = High
    """
    aerosol_value: bin = bin(pixel)[2:4]
    aerosol_value_int = int(aerosol_value, 2)
    return aerosol_value_int

def get_sensor_score(path):
    '''
    Checks which sensor the image is from
    Input:
    path: String, path to image
    Output:
    Integer, for Sentinel 0 for Landsat 1
    '''
    if "S30" in path:
        return 0
    if "L30" in path:
        return 1


# getDate and distance to target date from qa_layer path
def get_distance_to_target_date(path, target_date):
    '''
    Calculates distance to atrget dat
    Input:
    path: path to image
    target_date: data to which to calculate the distance to
    Output:
    Integer, days to target date
    '''
    sensing_date = utils.extract_sensing_date(gdal.Info(path))
    distance_to_target_date = abs(target_date - sensing_date)
    return distance_to_target_date.days


# get distance to cloud
def get_distance_to_cloud(pixel):
    '''
    Checks if pixel is adjacent to cloud
    Input:
    pixel: Binary, 8-Bit binary pixel value
    Output:
    Integer, 0 for is not adjacent, 1 for is adjacent
    '''
    """Adjacent cloud BitNumber: 2
    1 = Yes
    0 = No"""
    adjacent_cloud: bin = bin(pixel)[-3:-2]
    return int(adjacent_cloud)


def covered_by_cloud(pixel):
    '''
    Checks if pixel is covered by cloud, cirrus or cloud-sjadow
    Input:
    pixel: Binary, 8-Bit binary pixel value
    Output:
    Integer, 0 for is not covered, 1 for is covered
    '''
    cloudfree_pixel = [0, 4, 16, 20, 32, 36, 48, 52, 64, 68, 80, 84, 96,
                   100, 112, 116, 128, 132, 144, 148, 160, 164, 176, 180, 192, 196,
                   208, 212, 224, 228, 240, 244]
    if not int(pixel) in cloudfree_pixel:
        return 1
    else:
        return 0


def get_bap_score(pixel, distance_to_target_date, sensor_score):
    '''
    Calculates score for picel
    Input:
    pixel: Binary, 8-Bit binary pixel value
    distance_to_target_date: Integer: result from distance_target_date
    sensor_score: result from get_sensor_score
    Output:
    Integer, pixel score
    '''
    cloud_covered = covered_by_cloud(pixel)
    distance_to_cloud = get_distance_to_cloud(pixel)
    aerosol_quality = get_aerosol_quality(pixel)
    # print(f"cloud distance:{distance_to_cloud}, aerosol: {aerosol_quality}, date:{distance_to_target_date} cloud: {cloud_covered}")
    pixel_score = 5*distance_to_cloud + aerosol_quality + distance_to_target_date + 260*cloud_covered + 10*sensor_score
    return pixel_score


def main(path, qa_path, target_date):
    '''
    Calculates score for picel
    Input:
    path: String, path to image
    qa_path: String, path to qa_layer
    target_date: target date of bap
    Output:
    Array, with pixel scores for path
    '''
    print("start calculating bap for image: " + path)
    distance_target_date = get_distance_to_target_date(path, target_date)
    sensor_score = get_sensor_score(path)
    img = gdal.Open(qa_path)
    if img is not None:
        img_array = np.array(img.ReadAsArray())
        score_array = np.empty(img_array.shape)
        for index, pixel in np.ndenumerate(img_array):
            if pixel == None or pixel == np.nan or pixel == 0:
                score_array[index] = 260
            else:
                bap_score = get_bap_score(pixel, distance_target_date, sensor_score)
                if bap_score:
                    score_array[index] = bap_score
        distance_target_date=None
        img=None
        img_array = None
        return score_array
    else:
        return


if __name__ == "__main__":
    metadata = gdal.Info(testdataL30)
    distance_target_date = get_distance_to_target_date(testdataL30, datetime.datetime(2017, 7, 15))
    img = gdal.Open(testdataL30QA)
    img_array = np.array(img.ReadAsArray())
    bap_array = np.empty(img_array.shape)
    for indexrow, pixelrow in enumerate(img_array):
        for indexpixel, pixel in enumerate(pixelrow):
            bap_score = get_bap_score(pixel, testdataL30QA, distance_target_date)
            bap_array[indexrow, pixelrow] = bap_score
    utils.save_ind_img(testdataS30, bap_score, "bap", testdataS30)
