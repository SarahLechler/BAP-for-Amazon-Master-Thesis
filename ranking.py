from osgeo import gdal
import os
import utils

directoryPath = "../../../../scratch/tmp/s_lech05/hls_data/"


def create_list_of_files():
    filePathArray = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and (item == "21LYG" or item == "21LYH"):
            for year in os.listdir(tilePath):
                # if year == "2016" or year == "2017" or year == "2018":
                yearPath = os.path.join(tilePath, year)
                if os.path.isdir(yearPath):
                    for hlsDirectory in os.listdir(yearPath):
                        dirPath = os.path.join(yearPath, hlsDirectory)
                        if os.path.isdir(dirPath):
                            for file in os.listdir(dirPath):
                                if file.endswith('.hdf'):
                                    filePath = os.path.join(dirPath, file)
                                    filePathArray.append(filePath)
        elif os.path.isdir(tilePath) and (item == "2019"):
            yearPath = tilePath
            if os.path.isdir(yearPath):
                for hlsDirectory in os.listdir(yearPath):
                    dirPath = os.path.join(yearPath, hlsDirectory)
                    if os.path.isdir(dirPath):
                        for file in os.listdir(dirPath):
                            if file.endswith('.hdf'):
                                filePath = os.path.join(dirPath, file)
                                filePathArray.append(filePath)
    return filePathArray


def create_list_of_fileshdf5():
    filePathArray = []
    for item in os.listdir(directoryPath):
        tilePath = os.path.join(directoryPath, item)
        if os.path.isdir(tilePath) and (item == "21LYG" or item == "21LYH"):
            for year in os.listdir(tilePath):
                yearPath = os.path.join(tilePath, year)
                if os.path.isdir(yearPath):
                    for hlsDirectory in os.listdir(yearPath):
                        dirPath = os.path.join(yearPath, hlsDirectory)
                        if os.path.isdir(dirPath):
                            for file in os.listdir(dirPath):
                                if file.endswith('.h5'):
                                    filePath = os.path.join(dirPath, file)
                                    filePathArray.append(filePath)
    return filePathArray


def group_images_per_month(file_path_array):
    monthly_img2013H = [[]] * 12
    monthly_img2014H = [[]] * 12
    monthly_img2015H = [[]] * 12
    monthly_img2013G = [[]] * 12
    monthly_img2014G = [[]] * 12
    monthly_img2015G = [[]] * 12
    monthly_img2016H = [[]] * 12
    monthly_img2017H = [[]] * 12
    monthly_img2018H = [[]] * 12
    monthly_img2016G = [[]] * 12
    monthly_img2017G = [[]] * 12
    monthly_img2018G = [[]] * 12
    monthly_img2019G = [[]] * 12
    monthly_img2020G = [[]] * 12
    monthly_img2019H = [[]] * 12
    monthly_img2020H = [[]] * 12

    for file in file_path_array:
        year = utils.extract_sensing_year_from_filename(file)
        month = utils.extract_sensing_month_from_filename(file)
        if "21LYH" in file:
            if year == 2013:
                if not monthly_img2013H[month - 1]:
                    monthly_img2013H[month - 1] = [file]
                else:
                    monthly_img2013H[month - 1].append(file)
            if year == 2014:
                if not monthly_img2014H[month - 1]:
                    monthly_img2014H[month - 1] = [file]
                else:
                    monthly_img2014H[month - 1].append(file)
            if year == 2015:
                if not monthly_img2015H[month - 1]:
                    monthly_img2015H[month - 1] = [file]
                else:
                    monthly_img2015H[month - 1].append(file)
            if year == 2016:
                if not monthly_img2016H[month - 1]:
                    monthly_img2016H[month - 1] = [file]
                else:
                    monthly_img2016H[month - 1].append(file)
            if year == 2017:
                if not monthly_img2017H[month - 1]:
                    monthly_img2017H[month - 1] = [file]
                else:
                    monthly_img2017H[month - 1].append(file)
            if year == 2018:
                if not monthly_img2018H[month - 1]:
                    monthly_img2018H[month - 1] = [file]
                else:
                    monthly_img2018H[month - 1].append(file)
            if year == 2019:
                if not monthly_img2019H[month - 1]:
                    monthly_img2019H[month - 1] = [file]
                else:
                    monthly_img2019H[month - 1].append(file)
            if year == 2020:
                if not monthly_img2020H[month - 1]:
                    monthly_img2020H[month - 1] = [file]
                else:
                    monthly_img2020H[month - 1].append(file)
        if "21LYG" in file:
            if year == 2013:
                if not monthly_img2013G[month - 1]:
                    monthly_img2013G[month - 1] = [file]
                else:
                    monthly_img2013G[month - 1].append(file)
            if year == 2014:
                if not monthly_img2014G[month - 1]:
                    monthly_img2014G[month - 1] = [file]
                else:
                    monthly_img2014G[month - 1].append(file)
            if year == 2015:
                if not monthly_img2015G[month - 1]:
                    monthly_img2015G[month - 1] = [file]
                else:
                    monthly_img2015G[month - 1].append(file)
            if year == 2016:
                if not monthly_img2016G[month - 1]:
                    monthly_img2016G[month - 1] = [file]
                else:
                    monthly_img2016G[month - 1].append(file)
            if year == 2017:
                if not monthly_img2017G[month - 1]:
                    monthly_img2017G[month - 1] = [file]
                else:
                    monthly_img2017G[month - 1].append(file)
            if year == 2018:
                if not monthly_img2018G[month - 1]:
                    monthly_img2018G[month - 1] = [file]
                else:
                    monthly_img2018G[month - 1].append(file)
            if year == 2019:
                if not monthly_img2019G[month - 1]:
                    monthly_img2019G[month - 1] = [file]
                else:
                    monthly_img2019G[month - 1].append(file)
            if year == 2020:
                if not monthly_img2020G[month - 1]:
                    monthly_img2020G[month - 1] = [file]
                else:
                    monthly_img2020G[month - 1].append(file)
    monthly_img2013G = [x for x in monthly_img2013G if x != []]
    monthly_img2013H = [x for x in monthly_img2013H if x != []]
    return [monthly_img2013G, monthly_img2013H, monthly_img2014G, monthly_img2014H, monthly_img2015G, monthly_img2015H,
            monthly_img2016G, monthly_img2016H, monthly_img2017G, monthly_img2017H, monthly_img2018G, monthly_img2018H,
            monthly_img2019G, monthly_img2019H, monthly_img2020G, monthly_img2020H]


def create_cloud_ranking(imgArray):
    if imgArray != []:
        cloud_coverage = utils.extract_cloud_coverage(imgArray[0])
        spatial_coverage = utils.extract_spatial_coverage(imgArray[0])
        coverage = spatial_coverage - cloud_coverage
        best_path = imgArray[0]
    else:
        return
    for img in imgArray:
        if img is None:
            continue
        new_cloud_coverage = utils.extract_cloud_coverage(img)
        new_spatial_coverage = utils.extract_spatial_coverage(img)
        new_coverage = new_spatial_coverage - new_cloud_coverage
        if new_coverage > coverage:
            coverage = new_coverage
            best_path = img
    return best_path
