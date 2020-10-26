import numpy as np
import os
from osgeo import gdal
import datetime
import utils
import ranking

directoryPath = "../../../../scratch/tmp/s_lech05/hls_data/"


def get_indice_img_paths(indice_name, tile_name):
    filePathArray = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile_name:
            for year in os.listdir(tilePath):
                yearPath = os.path.join(tilePath, year)
                if os.path.isdir(yearPath):
                    for hlsDirectory in os.listdir(yearPath):
                        dirPath = os.path.join(yearPath, hlsDirectory)
                        if os.path.isdir(dirPath):
                            for indices_dir_path in os.listdir(dirPath):
                                indices_dir_path = os.path.join(dirPath, indices_dir_path)
                                if os.path.isdir(indices_dir_path):
                                    for file in os.listdir(indices_dir_path):
                                        if indice_name in file and ".xml" not in file and "classified" not in file and "training_data" not in file:
                                            filePath = os.path.join(indices_dir_path, file)
                                            month = utils.extract_sensing_month_from_filename(filePath)
                                            if (month < 7 and year == 2020) or year != 2020 or (
                                                    month > 7 and year == 2013):
                                                filePathArray.append(filePath)
    index_images = ranking.group_images_per_month(filePathArray)
    monthly_images = []
    for images in index_images:
        for months in images:
            ranking_results = ranking.create_cloud_ranking(months)
            monthly_images.append(ranking_results)
    return monthly_images


def get_pixel_value_array(img_array):
    first_data = gdal.Open(img_array[0])
    time_series_array = first_data.ReadAsArray()
    for img_path in img_array[1:]:
        data = gdal.Open(img_path)
        data_array = data.ReadAsArray()
        time_series_array = np.dstack((time_series_array, data_array))
    time_series_array = np.swapaxes(time_series_array, 0, 2)
    return time_series_array


def save_time_series(time_series, path):
    np.save(path, time_series)


def sortImgPahts(paths):
    dates = []
    for img in paths:
        dates.append(utils.extract_sensing_date_from_filename(img))
    dates = np.array(dates)
    paths = np.array(paths)
    imgDates = np.concatenate((dates.reshape(len(dates), 1), paths.reshape(len(paths), 1)), axis=1)
    imgDates = np.array(sorted(imgDates, key=lambda x: x[0]))
    dates = None
    paths = None
    return imgDates[:, 1]


# if __name__ == '__main__'
"""
creates a times series with the given image data
input:  index name String (NDVI, RNSDI, SAVI, GEMI EVI)
        tile name String (21LYG 21LYH)
        portion array with Integers describing the portion of the image
"""


def get_indice_bap_img_paths(index, tile, directoryPath):
    bap_images = []
    # make single for loops
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile:
            for year_folder in os.listdir(tilePath):
                year_path = os.path.join(tilePath, year_folder)
                if os.path.isdir(year_path):
                    for index_bap_files in os.listdir(year_path):
                        if index_bap_files.endswith(".tif") and index in index_bap_files:
                            index_path = os.path.join(year_path, index_bap_files)
                            month = utils.extract_sensing_month_from_filename(index_path)
                            year = utils.extract_sensing_year_from_filename(index_path)
                            if (month < 8 and year == 2020) or year != 2020 or year != 2013 or (
                                    month > 7 and year == 2013):
                                bap_images.append(index_path)
    return bap_images


def create_time_series(name, tile, bap):
    if bap:
        paths = get_indice_bap_img_paths(name, tile, "../../../../scratch/tmp/s_lech05/hls_data/")
    else:
        paths = get_indice_img_paths(name, tile)
    sortedImgPaths = sortImgPahts(paths)
    time_series = get_pixel_value_array(sortedImgPaths)
    print(f"Finish creating time_series for tile {tile} and index {name}")
    sortedImgPaths = None
    return time_series
