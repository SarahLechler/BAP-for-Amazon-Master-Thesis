import numpy as np
import os
from osgeo import gdal
import datetime
import utils
directoryPath = "./Images"

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
                                        if file.find(indice_name) != -1 and file.find(".xml") == -1 and file.find(
                                                "classified") == -1 and file.find(
                                                "training_data") == -1:
                                            filePath = os.path.join(indices_dir_path, file)
                                            month = utils.extract_sensing_month_from_filename(filePath)
                                            if month < 8 and year == 2018 or year != 2018:
                                                filePathArray.append(filePath)
    return filePathArray


def get_pixel_value_array(img_array):
    first_data = gdal.Open(img_array[0])
    time_series_array = first_data.ReadAsArray()
    for img_path in img_array [1:]:
        data = gdal.Open(img_path)
        data_array = data.ReadAsArray()
        np.vstack(time_series_array, data_array)
    """for img_index, img_path in enumerate(img_array, start=0):
        data = gdal.Open(img_path)
        data_array = data.ReadAsArray()
        
        for lat_index, lat_array in enumerate(data_array, start=0):
            for long_index, pixel in enumerate(lat_array, start=0):
                if (lat_index > rows - 1 or long_index > columns - 1):
                    break
                time_series_array[img_index][lat_index][long_index] = pixel"""
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
    yearly_images = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile:
            for year_folder in os.listdir(tilePath):
                year_path = os.path.join(tilePath, year_folder)
                for index_bap_files in os.listdir(year_path):
                    if index_bap_files.endswith(".tif") and index in index_bap_files:
                        index_path = os.path.join(year_path, index_bap_files)
                        yearly_images.append(index_path)
    return yearly_images


def create_time_series(name, tile, bap):
    if bap:
        paths = get_indice_bap_img_paths(name, tile, "hls_dataset")
    else:
        paths = get_indice_img_paths(name, tile)
    sortedImgPaths = sortImgPahts(paths)
    time_series = get_pixel_value_array(sortedImgPaths)
    print(f"Finish creating time_series for tile {tile} and index {name}")
    sortedImgPaths = None
    return time_series
