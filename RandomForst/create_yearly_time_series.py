import numpy as np
import os
import gdal
import matplotlib.pyplot as plt
import datetime

directoryPath = "../Images"


def extract_sensing_month(filepath):
    metadata = gdal.Info(filepath)
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        month = metadata[st_index + 18:st_index + 20]
        return int(month)


def get_indice_img_paths(indice_name, tile_name, y):
    filePathArray = []
    monthArray = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile_name:
            for year in os.listdir(tilePath):
                yearPath = os.path.join(tilePath, year)
                if os.path.isdir(yearPath) and (year == y[0] or year == y[1]):
                    for hlsDirectory in os.listdir(yearPath):
                        dirPath = os.path.join(yearPath, hlsDirectory)
                        if os.path.isdir(dirPath):
                            for indices_dir_path in os.listdir(dirPath):
                                indices_dir_path = os.path.join(dirPath, indices_dir_path)
                                if os.path.isdir(indices_dir_path):
                                    for file in os.listdir(indices_dir_path):
                                        if file.find(indice_name) != -1 and file.find(".xml") == -1:
                                            filePath = os.path.join(indices_dir_path, file)
                                            month = extract_sensing_month(filePath)
                                            if month and (
                                                    (month > 7 and year == y[1]) or (
                                                    month < 8 and year == y[0])) and filePath.find("classified") == -1:
                                                monthArray.append(str(month) + str(year))
                                                filePathArray.append(filePath)
    return filePathArray


def get_pixel_value_array(img_array, rows, columns):
    time_series_array = np.empty([rows, columns, len(img_array)])
    for img_index, img_path in enumerate(img_array, start=0):
        data = gdal.Open(img_path)
        data_array = data.ReadAsArray()
        for lat_index, lat_array in enumerate(data_array, start=0):
            for long_index, pixel in enumerate(lat_array, start=0):
                if (lat_index > rows - 1 or long_index > columns - 1):
                    break
                time_series_array[lat_index][long_index][img_index] = pixel
    return time_series_array


def save_time_series(time_series, path):
    print(f"saving time series to path {path}")
    time_series = time_series.flatten()
    np.save(path, time_series)


def plotTS(time_series, year, index, tile):
    plt.figure(figsize=(12, 12))
    for lat in time_series:
        for long in lat:
            plt.plot(long)
    #plt.plot(time_series[0,0,:])
    plt.title(f"TS for year: {year} and index {index}")
    plt.ylabel(f'{index} value')
    plt.xlabel('Time')
    plt.savefig(f'../Images/plots/ts{tile}{year}{index}_lineplot_multipixel')


# if __name__ == '__main__'

def extract_sensing_time(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        sensingTime = metadata[st_index + 13:st_index + 20]
        return datetime.date(int(sensingTime[0:4]), int(sensingTime[5:7]), 1)


def sortImgPahts(paths):
    dates = []
    for img in paths:
        img_metadata = gdal.Info(img)
        dates.append(extract_sensing_time(img_metadata))
    dates = np.array(dates)
    print(dates)
    paths = np.array(paths)
    print(paths)
    imgDates = np.concatenate((dates.reshape(len(dates), 1), paths.reshape(len(paths), 1)), axis=1)
    print(imgDates[0][0])
    imgDates = np.array(sorted(imgDates, key=lambda x: x[0]))
    print(imgDates)
    return imgDates[:, 1]

"""
creates a times series with the given image data
input:  index name String (NDVI, RNSDI, SAVI, GEMI EVI)
        tile name String (21LYG 21LYH)
        portion array with Integers describing the portion of the image
        year String
"""
def create_time_series(name, tile, portion, year):
    years = [str(year), str(year - 1)]
    path = get_indice_img_paths(name, tile, years)
    sortedPaths = sortImgPahts(path)
    time_series = get_pixel_value_array(sortedPaths, portion[0], portion[1])
    """save_time_series(time_series, directoryPath + "/" + tile + str(year) + name + ".npy")
    plotTS(time_series, year, name, tile)"""
    print(f"Finish creating time_series for tile {tile} and index {name} and has a shape of {time_series.shape}")
    return time_series

