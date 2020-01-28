import gdal
import numpy as np
from osgeo import gdal_array


def create_clear_sky_image(path):
    print(f"Start creating clear_sky images for file {path}")
    hls_dataset = gdal.Open(path)
    cloud_mask = gdal.Open(path + "cloud_mask.tif")
    cloud_mask_array = cloud_mask.ReadAsArray()
    invert_cloud_mask_array = np.zeros_like(cloud_mask_array)
    invert_cloud_mask_array[cloud_mask_array == 0] = 1
    invert_cloud_mask_array[cloud_mask_array == 1] = 0
    clear_sky_paths = []
    subdatasets = hls_dataset.GetSubDatasets()
    for dataset_path in subdatasets:
        dataset = gdal.Open(dataset_path[0])
        dataset_array = dataset.ReadAsArray()
        clear_sky_array = dataset_array * invert_cloud_mask_array
        template_file = dataset
        out_path = path[:-4] + "/" + dataset_path[0][-3:] + '_clear_sky.tif'
        clear_sky_paths.append(out_path)
        """clear_sky_file = gdal_array.SaveArray(clear_sky_array, out_path, format="GTiff", prototype=template_file)
        clear_sky_file = None"""
    print(f"Finished creating clear_sky images for file {path}")
    return clear_sky_paths
