from osgeo import gdal
import os

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



def extract_cloud_coverage(metadata):
    cc_index = metadata.find("cloud_coverage")
    if cc_index != -1:
        cloud_coverage = metadata[cc_index + 15:cc_index + 19]
        return int(cloud_coverage)


def extract_spatial_coverage(metadata):
    cc_index = metadata.find("spatial_coverage")
    if cc_index != -1:
        spatial_coverage = metadata[cc_index + 17:cc_index + 21]
        return int(spatial_coverage)


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

    for file in file_path_array:
        print(f"working with file {file}")
        file_metadata = gdal.Info(file)
        year = extract_sensing_year(file_metadata)
        month = extract_sensing_month(file_metadata)
        if file_metadata.find("21LYH") != -1:
            if year == "2013":
                if not monthly_img2013H[month - 1]:
                    monthly_img2013H[month - 1] = [file]
                else:
                    monthly_img2013H[month - 1].append(file)
            if year == "2014":
                if not monthly_img2014H[month - 1]:
                    monthly_img2014H[month - 1] = [file]
                else:
                    monthly_img2014H[month - 1].append(file)
            if year == "2015":
                if not monthly_img2015H[month - 1]:
                    monthly_img2015H[month - 1] = [file]
                else:
                    monthly_img2015H[month - 1].append(file)
            if year == "2016":
                if not monthly_img2016H[month - 1]:
                    monthly_img2016H[month - 1] = [file]
                else:
                    monthly_img2016H[month - 1].append(file)
            if year == "2017":
                if not monthly_img2017H[month - 1]:
                    monthly_img2017H[month - 1] = [file]
                else:
                    monthly_img2017H[month - 1].append(file)
            if year == "2018":
                if not monthly_img2018H[month - 1]:
                    monthly_img2018H[month - 1] = [file]
                else:
                    monthly_img2018H[month - 1].append(file)
        if file_metadata.find("21LYG") != -1:
            if year == "2013":
                if not monthly_img2013G[month - 1]:
                    monthly_img2013G[month - 1] = [file]
                else:
                    monthly_img2013G[month - 1].append(file)
            if year == "2014":
                if not monthly_img2014G[month - 1]:
                    monthly_img2014G[month - 1] = [file]
                else:
                    monthly_img2014G[month - 1].append(file)
            if year == "2015":
                if not monthly_img2015G[month - 1]:
                    monthly_img2015G[month - 1] = [file]
                else:
                    monthly_img2015G[month - 1].append(file)
            if year == "2016":
                if not monthly_img2016G[month - 1]:
                    monthly_img2016G[month - 1] = [file]
                else:
                    monthly_img2016G[month - 1].append(file)
            if year == "2017":
                if not monthly_img2017G[month - 1]:
                    monthly_img2017G[month - 1] = [file]
                else:
                    monthly_img2017G[month - 1].append(file)
            if year == "2018":
                if not monthly_img2018G[month - 1]:
                    monthly_img2018G[month - 1] = [file]
                else:
                    monthly_img2018G[month - 1].append(file)
    monthly_img2013G = [x for x in monthly_img2013G if x != []]
    monthly_img2013H = [x for x in monthly_img2013H if x != []]
    return [monthly_img2013G, monthly_img2013H, monthly_img2014G, monthly_img2014H, monthly_img2015G, monthly_img2015H, monthly_img2016G, monthly_img2016H, monthly_img2017G, monthly_img2017H, monthly_img2018G, monthly_img2018H]


def create_cloud_ranking(imgArray):
    if imgArray != []:
        file_metadata = gdal.Info(imgArray[0])
        cloud_coverage = extract_cloud_coverage(file_metadata)
        spatial_coverage = extract_spatial_coverage(file_metadata)
        coverage = spatial_coverage - cloud_coverage
        best_path = imgArray[0]
    else:
        return
    for img in imgArray:
        img_metadata = gdal.Info(img)
        new_cloud_coverage = extract_cloud_coverage(img_metadata)
        new_spatial_coverage = extract_spatial_coverage(img_metadata)
        new_coverage = new_spatial_coverage - new_cloud_coverage
        if new_coverage > coverage:
            coverage = new_coverage
            best_path = img
    return best_path
