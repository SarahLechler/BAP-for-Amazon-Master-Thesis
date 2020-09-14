import gdal, ogr
import os

testpath = "../../../../scratch/tmp/s_lech05/hls_data/21LYH/2016/S30/HLS.S30.T21LYH.2016353.v1.4.hdf"  # "./hls_downloads\21LYH\2016\S30\HLS.S30.T21LYH.2016013.v1.4.hdf" './hls_downloads/21LYH/2016/L30/HLS.L30.T21LYH.2016014.v1.4.hdf'

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

"""
creates single band GeoTif from the given bandpath
input: dataset: path to band, hdf_path: path to generall file
"""

def create_singleband_geotif(dataset, hdf_path):
    h5spot = hdf_path.find('.h5')
    folder_path = hdf_path[:h5spot]
    if ".L30." in str(hdf_path):
        if "QA" in dataset:
            band = "QA"
        else:
            band = dataset[-6:]
        datasetFirst = dataset.find('HLS.L30')
        datsaetLast = dataset.find('v1.4')
        path = dataset[datasetFirst:datsaetLast + 4]
        band_path = band.replace(band, BAND_NAMES["L30"][band])
    elif ".S30." in str(hdf_path):
        if "QA" in dataset:
            band = "QA"
        else:
            band = dataset[-3:]
        datasetFirst = dataset.find('HLS.S30')
        datsaetLast = dataset.find('v1.4')
        path = dataset[datasetFirst:datsaetLast + 4]
        band_path = band.replace(band, BAND_NAMES["S30"][band])
    else:
        return
    file_path = folder_path + '/' + path + '_' + band_path + '.tif'
    print("saved to: " + file_path)
    if os.path.isfile(file_path):
        return
    gdal.Translate(file_path, dataset, options=[("-of"), ("GTiff")])


"""
    creates multi band GeoTif 
    input: path: hdf file path
"""

def create_multiband_geotif(path):
    hdf_dataset = gdal.Open(path)
    subdatasets = hdf_dataset.GetSubDatasets()
    if not (os.path.isdir(path[:-3])):
        os.mkdir(path[:-3])
    for dataset in subdatasets:
        print("starting translating")
        create_singleband_geotif(dataset[0], path)
    hdf_dataset = None


if __name__ == '__main__':
    create_multiband_geotif(testpath)
