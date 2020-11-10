from osgeo import gdal
import matplotlib.pyplot as plt
from osgeo import gdal_array
import numpy as np
import nasa_hls


def retrieve_cloud_mask_from_QA(hf_file):
    hf_dataset = gdal.Open(hf_file)
    if not hf_dataset:
        return
    if hf_file.find("L30") != -1:
        qa_layer_path = hf_dataset.GetSubDatasets()[10][0]
    else:
        qa_layer_path = hf_dataset.GetSubDatasets()[13][0]
    qa_layer = gdal.Open(qa_layer_path)
    qa_array = qa_layer.ReadAsArray()
    valid_pixel = [0, 4, 16, 20, 32, 36, 48, 52, 64, 68, 80, 84, 96,
                   100, 112, 116, 128, 132, 144, 148, 160, 164, 176, 180, 192, 196,
                   208, 212, 224, 228, 240, 244]
    mask_array = np.zeros_like(qa_array)
    for num in valid_pixel:
        mask_array[qa_array == num] = 1
    """cirrus = qa_array % 2
    qa_array = qa_array // 2
    cloud = qa_array % 2
    qa_array = qa_array // 2
    adjacent = qa_array % 2
    qa_array = qa_array // 2
    cloud_shadow = qa_array % 2

    contaminated = cloud + cloud_shadow + cirrus
    binary_mask = (contaminated > 0).astype(int)"""
    return mask_array


def plot_mask(mask):
    fig, ax = plt.subplots()
    im = ax.imshow(mask)
    plt.show()


def save_cloud_mask(path, cloud_mask):
    out_path = path[:-3] + "/" + "cloud_mask.tif"
    if path.find("cirrus") != -1:
        path = path[:-6]
    if path.find("cloud") != -1:
        path = path[:-5]
    if path.find("shadow") != -1:
        path = path[:-6]
    if path.find("adj") != -1:
        path = path[:-3]
    if path.find('LYH') != -1:
        template_file = '/scratch/tmp/s_lech05/hls_data/21LYH/template_file_21LYH.tif'
    else:
        template_file = '/scratch/tmp/s_lech05/hls_data/21LYG/template_file_21LYG.tif'
    output = gdal_array.SaveArray(cloud_mask, out_path, format="GTiff", prototype=template_file)
    output = None


def create_cloudmask(path):
    if not path:
        return
    mask = retrieve_cloud_mask_from_QA(path)
    if mask is not None:
        save_cloud_mask(path, mask)
