"""TODO:
Get "main image from the image with the highest score the
closest to the 15. of each month

Get next images that are timely shifted and evaluate pixel
that are missing in main image --> do this recursive until
image is fully filled or images are farther away than 10 days
"""
import os
import gdal
import numpy as np
import datetime

import bap_score
import utils


def get_images_of_month(month, year, directoryPath, tile):
    monthly_images = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile:
            for year_folder in os.listdir(tilePath):
                if int(year_folder) == year:
                    year_path = os.path.join(tilePath, year_folder)
                    for hlsDirectory in os.listdir(year_path):
                        dirPath = os.path.join(year_path, hlsDirectory)
                        if os.path.isdir(dirPath):
                            for file in os.listdir(dirPath):
                                if file.endswith('.h5'):
                                    filePath = os.path.join(dirPath, file)
                                    metadata = gdal.Info(filePath)
                                    if metadata == None:
                                        continue
                                    file_month = utils.extract_sensing_month(metadata)
                                    if file_month == month:
                                        monthly_images.append(filePath)
    return monthly_images


def list_index(index, monthly_images):
    index_list = []
    for image in monthly_images:
        for file in os.listdir(image[:-3]):
            if index in file and not "BAP" in file:
                print(file)
                index_img = gdal.Open(os.path.join(image[:-3], file))
                index_list.append(index_img.ReadAsArray())
    return index_list


def main(month, year, foldername, tile, indices):
    monthly_images = get_images_of_month(month, year, foldername, tile)
    bap_stack = []
    for image in monthly_images:
        qa_layer_path = image[:-3] + "/QA_clear_sky.tif"
        for layer in os.listdir(image[:-3]):
            if "QA" in layer and "clear" in layer:
                qa_layer_path = os.path.join(image[:-3], layer)
        bap_array = bap_score.main(image, qa_layer_path, datetime.datetime(year, month, 15))
        bap_stack.append(bap_array)
    bap_array = np.array(bap_stack)
    print(bap_array)
    if bap_array.size == 0:
        return
    bpa_pixel = np.argmin(bap_array, axis=0)
    for index in indices:
        if os.path.isfile(monthly_images[0][:-35] + "/" + index + "_BAP_" + str(month) + ".tif"):
            continue
        index_array = np.array(list_index(index, monthly_images))
        index_bpa = np.choose(bpa_pixel, index_array)
        utils.save_ind_img(monthly_images[0][:-35], index_bpa, index + "_BAP_" + str(month),
                           monthly_images[0][:-3] + "/NDVI.tif", True)
        print(f"BAP calculated for {month} {year} for {index}")


if __name__ == "__main__":
    """years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    months = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]"""

    monthly_images = get_images_of_month(5, 2017, "hls_dataset", "21LYG")
    bap_stack = []
    for image in monthly_images:
        qa_layer_path = image[:-3] + "/QA_clear_sky.tif"
        for layer in os.listdir(image[:-3]):
            if "QA" in layer and "clear" in layer:
                qa_layer_path = os.path.join(image[:-3], layer)
        print(qa_layer_path)
        bap_array = bap_score.main(image, qa_layer_path, datetime.datetime(2017, 1, 15))
        print(bap_array)
        bap_stack.append(bap_array)
    bap_array = np.array(bap_stack)
    print(bap_array.shape)
    bpa_pixel = np.argmin(bap_array, axis=0)
    # utils.save_ind_img(monthly_images[0][:-3], np.int(bpa_pixel), "argmin" + "January", monthly_images[0][:-3] + "/NDVI.tif", True)
    print(bpa_pixel.shape)
    ndvi_array = np.array(list_index("NDVI", monthly_images))
    print(ndvi_array.shape)
    index_bpa = np.choose(bpa_pixel, ndvi_array)
    utils.save_ind_img(monthly_images[0][:-35], index_bpa, "NDVI_BAP", monthly_images[0][:-3] + "/NDVI.tif", True)
