import numpy as np
import os
import gdal
import matplotlib.pyplot as plt
import datetime
import utils
import ranking



def get_indice_img_paths(indice_name, tile_name, y, directoryPath):
    filePathArray = []
    monthArray = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile_name:
            for year in os.listdir(tilePath):
                yearPath = os.path.join(tilePath, year)
                if os.path.isdir(yearPath) and (int(year) == y[0] or int(year) == y[1]):
                    for hlsDirectory in os.listdir(yearPath):
                        dirPath = os.path.join(yearPath, hlsDirectory)
                        if os.path.isdir(dirPath):
                            for indices_dir_path in os.listdir(dirPath):
                                indices_dir_path = os.path.join(dirPath, indices_dir_path)
                                if os.path.isdir(indices_dir_path):
                                    for file in os.listdir(indices_dir_path):
                                        if file.find(indice_name) != -1 and file.find(".xml") == -1:
                                            filePath = os.path.join(indices_dir_path, file)
                                            month = utils.extract_sensing_month_from_filename(filePath)
                                            if month and (
                                                    (month > 7 and int(year) == y[1]) or (
                                                    month < 8 and int(year) == y[0])) and filePath.find(
                                                "classified") == -1:
                                                monthArray.append(str(month) + str(year))
                                                filePathArray.append(filePath)
    index_images = ranking.group_images_per_month(filePathArray, tile_name)
    monthly_images = []
    for images in index_images:
        for months in images:
            print(months)
            if months:
                ranking_results = ranking.create_cloud_ranking(months)
                monthly_images.append(ranking_results)
    return monthly_images


def get_indice_bap_img_paths(index, tile, directoryPath, y):
    yearly_images = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile:
            for year_folder in os.listdir(tilePath):
                year_path = os.path.join(tilePath, year_folder)
                if os.path.isdir(year_path) and (int(year_folder) == y[0] or int(year_folder) == y[1]):
                    for index_bap_files in os.listdir(year_path):
                        if index_bap_files.endswith(".tif") and index in index_bap_files:
                            index_path = os.path.join(year_path, index_bap_files)
                            month = utils.extract_sensing_month_from_filename(index_path)
                            if month and (
                                    (month > 7 and year_folder == str(y[1])) or (
                                    month < 8 and year_folder == str(y[0]))) and "classified" not in index_path:
                                yearly_images.append(index_path)
    return yearly_images


def get_pixel_value_array(img_array):
    first_data = gdal.Open(img_array[0])
    time_series_array = first_data.ReadAsArray()
    for img_path in img_array[1:]:
        data = gdal.Open(img_path)
        data_array = data.ReadAsArray()
        time_series_array = np.dstack((time_series_array, data_array))
    # time_series_array = np.swapaxes(time_series_array, 0, 2)
    return time_series_array


def save_time_series(time_series, path):
    print(f"saving time series to path {path}")
    time_series = time_series.flatten()
    np.save(path, time_series)


def plotTS(time_series, year, index, tile):
    time_series = np.where(time_series == -9999, np.nan, time_series)
    plt.figure(figsize=(12, 12))
    for lat in time_series:
        for long in lat:
            plt.plot(long)
    # plt.plot(time_series[0,0,:])
    plt.title(f"TS for year: {year} and index {index}")
    plt.ylabel(f'{index} value')
    plt.xlabel('Time')
    plt.savefig(f'../Images/plots/ts{tile}{year}{index}_lineplot_multipixel')


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


"""
creates a times series with the given image data
input:  index name String (NDVI, RNSDI, SAVI, GEMI EVI)
        tile name String (21LYG 21LYH)
        portion array with Integers describing the portion of the image
        year String
"""


def create_time_series(name, tile, year, bap, path):
    years = [year, year - 1]
    if bap:
        path = get_indice_bap_img_paths(name, tile, path, years)
    else:
        path = get_indice_img_paths(name, tile, years, path)
    sortedPaths = sortImgPahts(path)
    time_series = get_pixel_value_array(sortedPaths)
    nancount = np.count_nonzero(time_series == -9999)
    print(f"Finish creating time_series for tile {tile} and index {name} and {year} has a shape of {time_series.shape}. The number of nodata values for {bap} are: {nancount}")
    """save_time_series(time_series, directoryPath + "/" + tile + str(year) + name + ".npy")
    plotTS(time_series, year, name, tile)"""
    return time_series
