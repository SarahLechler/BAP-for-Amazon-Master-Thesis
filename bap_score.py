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


# get aerosol quality
def get_qa_layer(path):
    folder_path = path[:-3]
    bands_list = os.listdir(folder_path)
    qa_path = ""
    for band in bands_list:
        if "_QA" in str(band):
            qa_path = os.path.join(folder_path, band)
    return qa_path


"""
Aersol Quality: the 7&6 bit Number
00 = Climatology
01 = Low
10 = Average
11 = High
"""


def get_aerosol_quality(path, pixel):
    aerosol_value: bin = bin(pixel)[2:4]
    print(int(aerosol_value, 2))
    return int(aerosol_value, 2)
    """if aerosol_value == 0b00:
        return 0
    elif aerosol_value == 0b01:
        return 1
    elif aerosol_value == 0b10:
        return 2
    elif aerosol_value == 0b11:
        return 3"""



# getDate and distance to target date
def get_distance_to_target_date(path, target_date):
    metadata = gdal.Info(path)
    sensing_date = extractMetadataInformation.extract_sensing_date(metadata)
    distance_to_target_date = abs(target_date - sensing_date)
    return distance_to_target_date.days


# get distance to cloud
"""Adjacent cloud BitNumber: 2
1 = Yes
0 = No"""


def get_distance_to_cloud(pixel):
    """qa_layer = gdal.Open(path)
    qa_value: int = int(qa_layer[pixel])"""
    adjacent_cloud: bin = bin(pixel)[-3:-2]
    return int(adjacent_cloud)


def get_bap_score(pixel, path, distance_to_target_date):
    distance_to_cloud = get_distance_to_cloud(pixel)
    aerosol_quality = get_aerosol_quality(path, pixel)
    print(f"cloud:{distance_to_cloud}, aerosol: {aerosol_quality}, date:{distance_to_target_date}")
    return distance_to_cloud + aerosol_quality + distance_to_target_date


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
