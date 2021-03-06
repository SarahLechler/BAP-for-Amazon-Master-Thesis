import os
import gdal
import numpy as np
import datetime

import bap_score
import utils


def get_images_of_month(month, year, directoryPath, tile):
    '''
    Gets all images for a given month and a given year
    Input:
    month: Integer, month to get images for
    year: Integer, year to get images for
    directoryPath: String, path to directory where images are stored
    tile: String, tilename to get images for
    Output:
    Array[] with images for given month and year and tile
    '''
    monthly_images = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and item == tile:
            for year_folder in os.listdir(tilePath):
                if os.path.isdir(os.path.join(tilePath, year_folder)):
                    if int(year_folder) == year:
                        year_path = os.path.join(tilePath, year_folder)
                        for hlsDirectory in os.listdir(year_path):
                            dirPath = os.path.join(year_path, hlsDirectory)
                            if os.path.isdir(dirPath):  # and "S30" in dirPath
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
    '''
    Create list of index images
    Input:
    index: String, name of index
    monthly_images: Array[] of all images for which to get the index values
    Output:
    Array with index array for the month
    '''
    index_list = []
    for image in monthly_images:
        for file in os.listdir(image[:-3]):
            if index in file and not "BAP" in file:
                index_img = gdal.Open(os.path.join(image[:-3], file))
                index_list.append(index_img.ReadAsArray())
    return index_list


def calcSensorPixel(bap_min, monthly_images):
    '''
    Calculates occurence of pixel for each sensor
    Input:
    bap_min: Array[] with the position of the bap
    monthly_images: Array[] of monthly images
    Output:
    occurencesS30: number of pixels that are from Sentinel
    occurence L30: number of pixels that are from Landsat
    '''
    sensor_array = []
    for img in monthly_images:
        if "S30" in img:
            s30_array = np.full((bap_min.shape), 10)  # 10 = S30
            sensor_array.append(s30_array)
        if "L30" in img:
            l30_array = np.full((bap_min.shape), 20)  # 20=L30
            sensor_array.append(l30_array)
    sensor_bpa = np.choose(bap_min, sensor_array)
    occurrencesS30 = np.count_nonzero(sensor_bpa == 10)
    occurrencesL30 = np.count_nonzero(sensor_bpa == 20)
    return [occurrencesS30, occurrencesL30]


def main(month, year, foldername, tile, indices, overwrite):
    '''
    Creates composites based on the best available pixel
    Input:
    month: Integer, month to get images for
    year: Integer, year to get images for
    foldername: String, path to directory where images are stored
    tile: String, tilename to get images forOutput:
    indices: Array[], names inf indices
    overwrite: Boolean, whether to overwrite images or not
    Breaks and mean of time series
    '''
    monthly_images = get_images_of_month(month, year, foldername, tile)
    if monthly_images == []:
        print(f"No images exist  for {month} in {year} for tile {tile}")
        return
    bap_stack = []
    for image in monthly_images:
        qa_layer_path = image[:-3] + "/QA_clear_sky.tif"
        for layer in os.listdir(image[:-3]):
            if "QA" in layer and "clear" in layer:
                qa_layer_path = os.path.join(image[:-3], layer)
        bap_array = bap_score.main(image, qa_layer_path, datetime.datetime(year, month, 15))
        bap_stack.append(bap_array)
    bap_array = np.array(bap_stack)
    if bap_array.size == 0:
        return
    bap_array = np.where(np.isnan(bap_array), 300, bap_array)
    bpa_pixel = np.argmin(bap_array, axis=0)
    day = utils.extract_sensing_day(gdal.Info(qa_layer_path))
    for index in indices:
        if not overwrite and os.path.isfile(f"{monthly_images[0][:-35]}/{index}_BAP_d{day}m{month}y{year}.tif"):
            return
        index_array = np.array(list_index(index, monthly_images))
        index_bpa = np.choose(bpa_pixel, index_array)
        #utils.save_ind_img(monthly_images[0][:-35], index_bpa, index + "_BAP_", tile, True, gdal.Info(qa_layer_path))
        sensor_occurence = calcSensorPixel(bpa_pixel, monthly_images)
        print(
            f"BAP calculated for {month} {year} for {index}. It was calculated based on {len(monthly_images)}  images.{sensor_occurence[0]} pixels are from Sentinel images, {sensor_occurence[1]} are from Landsat")
    monthly_images = None
    bap_stack = None
    bap_array = None
    bpa_pixel = None
    index_array = None
    index_bpa = None


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
