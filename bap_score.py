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
import extractMetadataInformation
import utils


# get aerosol quality
def get_qa_layer(path):
    folder_path = path[:-3]
    bands_list = os.listdir(folder_path)
    qa_path = ""
    for band in bands_list:
        if "_QA" in str(band):
            qa_path = os.path.join(folder_path, band)
    return qa_path


def get_aerosol_quality(pixel):
    """
    Aersol Quality: the 7&6 bit Number
    00 = Climatology
    01 = Low
    10 = Average
    11 = High
    """
    aerosol_value: bin = bin(pixel)[2:4]
    print(int(aerosol_value, 2))
    aerosol_value_int = int(aerosol_value, 2)
    if aerosol_value_int == 0:
        return 3
    elif aerosol_value_int == 1:
        return 2
    elif aerosol_value_int == 2:
        return 1
    elif aerosol_value_int == 3:
        return 0


# getDate and distance to target date
def get_distance_to_target_date(path, target_date):
    metadata = gdal.Info(path)
    sensing_date = extractMetadataInformation.extract_sensing_date(metadata)
    distance_to_target_date = abs(target_date - sensing_date)
    return distance_to_target_date.days


# get distance to cloud
def get_distance_to_cloud(pixel):
    """Adjacent cloud BitNumber: 2
    1 = Yes
    0 = No"""
    adjacent_cloud: bin = bin(pixel)[-3:-2]
    return int(adjacent_cloud)


def covered_by_cloud(pixel):
    cloud_pixel = [0, 4, 16, 20, 32, 36, 48, 52, 64, 68, 80, 84, 96,
                   100, 112, 116, 128, 132, 144, 148, 160, 164, 176, 180, 192, 196,
                   208, 212, 224, 228, 240, 244]
    if int(pixel) in cloud_pixel:
        return 255
    else:
        return 0


def get_bap_score(pixel, path, distance_to_target_date):
    cloud_covered = covered_by_cloud(pixel)
    distance_to_cloud = get_distance_to_cloud(pixel)
    aerosol_quality = get_aerosol_quality(pixel)
    print(f"cloud:{distance_to_cloud}, aerosol: {aerosol_quality}, date:{distance_to_target_date} cloud: {cloud_covered}")
    return distance_to_cloud + aerosol_quality + distance_to_target_date + cloud_covered


def main(path, qa_path):
    metadata = gdal.Info(path)
    distance_target_date = get_distance_to_target_date(path, datetime.datetime(2016, 8, 15))
    img = gdal.Open(qa_path)
    img_array = np.array(img.ReadAsArray())
    bap_array = np.empty(img_array.shape)
    for indexrow, pixelrow in enumerate(img_array):
        for indexpixel, pixel in enumerate(pixelrow):
            bap_score = get_bap_score(pixel, qa_path, distance_target_date)
            bap_array[indexrow, pixelrow] = bap_score
    return bap_array


if __name__ == "__main__":
    metadata = gdal.Info(testdataL30)
    distance_target_date = get_distance_to_target_date(testdataL30, datetime.datetime(2016, 8, 15))
    img = gdal.Open(testdataL30QA)
    img_array = np.array(img.ReadAsArray())
    bap_array = np.empty(img_array.shape)
    for indexrow, pixelrow in enumerate(img_array):
        for indexpixel, pixel in enumerate(pixelrow):
            bap_score = get_bap_score(pixel, testdataL30QA, distance_target_date)
            bap_array[indexrow, pixelrow] = bap_score
    utils.save_ind_img(testdataS30, bap_score, "bap", testdataS30)
