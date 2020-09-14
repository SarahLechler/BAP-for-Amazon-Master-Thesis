from osgeo import gdal
import matplotlib.pyplot as plt
from osgeo import gdal_array
import numpy as np


def retrieve_cloud_mask_from_QA(hf_file):
    hf_dataset = gdal.Open(hf_file)
    if not hf_dataset:
        return
    if hf_file.find("L30") != -1:
        qa_layer_path = hf_dataset.GetSubDatasets()[10][0]
        print("qa path: " + qa_layer_path)
    else:
        qa_layer_path = hf_dataset.GetSubDatasets()[13][0]
        print("qa path: " + qa_layer_path)
    qa_layer = gdal.Open(qa_layer_path)
    qa_array = qa_layer.ReadAsArray()
    valid_pixel = [0, 4, 16, 20, 32, 36, 48, 52, 64, 68, 80, 84, 96,
                   100, 112, 116, 128, 132, 144, 148, 160, 164, 176, 180, 192, 196,
                   208, 212, 224, 228, 240, 244]
    mask_array = np.zeros_like(qa_array)
    for num in valid_pixel:
        mask_array[qa_array == num] = 1
    cirrus = qa_array % 2
    qa_array = qa_array // 2
    cloud = qa_array % 2
    qa_array = qa_array // 2
    adjacent = qa_array % 2
    qa_array = qa_array // 2
    cloud_shadow = qa_array % 2

    contaminated = cloud + cloud_shadow + cirrus
    binary_mask = (contaminated > 0).astype(int)
    return binary_mask, cirrus, cloud, adjacent, cloud_shadow


def plot_mask(mask):
    print(mask)
    fig, ax = plt.subplots()
    im = ax.imshow(mask)
    plt.show()


def save_cloud_mask(path, cloud_mask):
    out_path = path[:-3]+"/" +"cloud_mask.tif"
    if path.find("cirrus") != -1:
        path = path[:-6]
    if path.find("cloud") != -1:
        path = path[:-5]
    if path.find("shadow") != -1:
        path = path[:-6]
    if path.find("adj") != -1:
        path = path[:-3]
    hdf_dataset = gdal.Open(path)
    if path.find("L30") != -1:
        qa_layer_path = hdf_dataset.GetSubDatasets()[10][0]
    else:
        qa_layer_path = hdf_dataset.GetSubDatasets()[13][0]
    template_file = qa_layer_path
    print(f"saved file to {out_path}")
    output = gdal_array.SaveArray(cloud_mask, out_path, format="GTiff", prototype=template_file)
    output = None


def create_cloudmask(path):
    if not path:
        return
    masks = retrieve_cloud_mask_from_QA(path)
    mask = masks[0]
    # plot_mask(mask)
    save_cloud_mask(path, mask)
