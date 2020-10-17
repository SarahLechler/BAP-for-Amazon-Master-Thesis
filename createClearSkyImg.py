from osgeo import gdal
import numpy as np
from osgeo import gdal_array
import os

"""
dictionary to properly name image bands
"""
BAND_NAMES = {'S30': {'B01': 'Coastal_Aerosol',
                      'B02': 'Blue',
                      'B03': 'Green',
                      'B04': 'Red',
                      'B05': 'Red_Edge1',
                      'B06': 'Red_Edge2',
                      'B07': 'Red_Edge3',
                      'B08': 'NIR_Broad',
                      'B8A': 'NIR_Narrow',
                      'B09': 'Water_Vapor',
                      'B10': 'Cirrus',
                      'B11': 'SWIR1',
                      'B12': 'SWIR2',
                      'QA': 'QA'},
              'L30': {'band01': 'Coastal_Aerosol',
                      'band02': 'Blue',
                      'band03': 'Green',
                      'band04': 'Red',
                      'band05': 'NIR',
                      'band06': 'SWIR1',
                      'band07': 'SWIR2',
                      'band09': 'Cirrus',
                      'band10': 'TIRS1',
                      'band11': 'TIRS2',
                      'QA': 'QA'}}


def create_clear_sky_image(path):
    hls_dataset = gdal.Open(path)
    cloud_mask = gdal.Open(path[:-3] + "/cloud_mask.tif")
    if not cloud_mask:
        return
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
        out_path = path[:-3] + "/" + dataset_path[0][-3:] + '_clear_sky.tif'
        if (os.path.isfile(out_path)):
            clear_sky_paths.append(out_path)
            continue
        clear_sky_file = gdal_array.SaveArray(clear_sky_array, out_path, format="GTiff", prototype=template_file)
        clear_sky_file = None
    print(f"Finished creating clear_sky images for file {path}")
    return clear_sky_paths
