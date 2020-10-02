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

import extractMetadataInformation
import bap_score

def get_images_of_month(month, year, directoryPath):
    monthly_images = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and (item == "21LYG" or item == "21LYH"):
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
                                    file_month = extractMetadataInformation.extract_sensing_month(metadata)
                                    if file_month == month:
                                        monthly_images.append(filePath)
    return monthly_images


def get_main_image(monthly_images):
    distance_to_target = 10
    main_image = ""
    for image in monthly_images:
        day = extractMetadataInformation.extract_sensing_day(gdal.Info(image))
        if day == 15:
            main_image = image
        elif abs(day - 15) < distance_to_target:
            distance_to_target = day
            main_image = image
    return main_image

if __name__ == "__main__":
    years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    months = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]
    for year in years:
        for month in months:
            monthly_images = get_images_of_month(month, year, "hls_downloads")
            """main_image = get_main_image(monthly_images)
            monthly_images.remove(main_image)
            print(main_image)"""
            bap_stack = []
            for image in monthly_images:
                qa_layer_path = image[:-2] + "/QA_clear_sky.tif"
                for layer in os.listdir(image[:-2]):
                    if "QA" in layer & "clear":
                        qa_layer_path = os.path.join(image[:-2], layer)
                print(qa_layer_path)
                bap_array = bap_score.main(image, qa_layer_path)
                bap_stack.append(bap_array)
            print(bap_stack)

    monthly_images = get_images_of_month(6, 2016, "hls_downloads")
    """main_image = get_main_image(monthly_images)
    monthly_images.remove(main_image)
    print(main_image)"""
    bap_stack = []
    for image in monthly_images:
        qa_layer_path = image[:-2] + "/QA_clear_sky.tif"
        for layer in os.listdir(image[:-2]):
            if "QA" in layer & "clear":
                qa_layer_path = os.path.join(image[:-2], layer)
        print(qa_layer_path)
        bap_array = bap_score.main(image, qa_layer_path)
        bap_stack.append(bap_array)
    print(bap_stack)

    #TODO: sort images per day
    #TODO: run bap scores on adjacent images and fill gaps with high ranked pixel -> recursive
