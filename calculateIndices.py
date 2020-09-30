from osgeo import gdal_array
from osgeo import gdal
import numpy as np
import os


def applyCloudMask(ndvi, index_array):

    #mask out clouds based on ndvi since its the only one that gets it right

    clear_sky_array = np.where(np.isnan(ndvi), np.nan, index_array)
    print(np.count_nonzero(np.isnan(clear_sky_array)))
    return clear_sky_array


"""
Normalized vegetetation index
formula: (NIR-RED)/(NIR+RED)
Range: -1 and 1
"""


def calculate_ndvi(nir, red):
    ndvi = (nir - red) / (nir + red)
    ndvi = np.where(ndvi > 1, 1, ndvi)
    ndvi = np.where((ndvi < -1) & (ndvi != -999), -1, ndvi)

    return ndvi


'''
calculate evi as described in Schulty 2016
with coefficients C1=6, C2 = 7.5 and senso gain factor G = 2,5
adjustment of canopz background L =1
Enhanced Vegetation Index = EVI = 2.5*((NIR−RED)(NIR+6RED−7.5BLUE)+1)
Range: -1 and 1
'''


def calculate_evi(nir, red, blue):
    evi = 2.5 * ((nir - red) / (nir + 6 * red - 7.5 * blue + 1))
    evi = np.where(evi > 1, 1, evi)
    evi = np.where((evi < -1) & (evi != -999), -1, evi)
    return evi


'''
calculate GEMI
Global Environment Monitoring Index = GEMI = (n(1−0.25n)−(RED−0.125)(1−RED)) with 
n = ( 2 * ( NIR ^2 - RED ^2) + 1.5 * NIR + 0.5 * RED ) / ( NIR + RED + 0.5 ) 
Range -1 and 1
'''


def calculate_gemi(nir, red):
    n = (2 * (nir ^ 2 - red ^ 2) + 1.5 * nir + 0.5 * red) / (nir + red + 0.5)
    gemi = n * (1 - 0.25 * n) - ((red - 0.125) / (1 - red))
    gemi = np.where(gemi > 1, 1, gemi)
    gemi = np.where((gemi < -1) & (gemi != -999), -1, gemi)
    return gemi


'''
calculates Soil Adjusted Vegetation Index  (SAVI) with formula:
(NIR−Red)/(NIR+Red+L)*(1+L) with variables: L = 0,5 (between -0,9 and 1,6)
Range: 0 to 1
'''


def calculate_savi(nir, red):
    savi = (nir - red) / (nir + red + 0.5) * (1 + 0.5)
    savi = np.where(savi > 1, 1, savi)
    savi = np.where((savi < 0) & (savi != -999), 0, savi)
    return savi


'''
calculates normalized Normalized Difference Soil index (NDSI) with formula:
    ndsi = (swir2 - green) / (swir2 + green)
can seperate soil from other landcover types
'''


def calculate_nndsi(swir2, green):
    ndsi = (swir2 - green) / (swir2 + green)
    nndsi = (ndsi - np.min(ndsi)) / (np.max(ndsi) - np.min(ndsi))
    return nndsi


'''
calculates normalized Tasseled Cap transforamation for brightness with formula:
    0.3037(CA) + 0.2793(BLUE) + 0.4743(GREEN) + 0.5585(RED) + 0.5082(NIR) + 0.1863(SWIR2) 

'''


def calculate_ntcb(ca, blue, green, red, nir, swir2):
    tcb = 0.3037 * ca + 0.2793 * blue + 0.4743 * green + 0.5585 * red + 0.5082 * nir + 0.1863 * swir2
    ntcb = (tcb - np.min(tcb)) / (np.max(tcb) - np.min(tcb))
    return ntcb


'''
calculates ratio Normalized Difference Soil index (RNDSI) with formula:
    ndsi = (swir2 - green) / (swir2 + green)

'''


def calculate_rndsi(ca, blue, green, red, nir, swir2):
    nndsi = calculate_nndsi(swir2, green)
    ntcb = calculate_ntcb(ca, blue, green, red, nir, swir2)
    rndsi = nndsi / ntcb
    return rndsi


def save_ind_img(path, ind, name, template_file):
    out_path = path + name + '.tif'
    if (os.path.isfile(out_path)):
        return
    # print(f"saved file to {out_path}")
    ind_output = gdal_array.SaveArray(ind, out_path, format="GTiff", prototype=template_file)
    ind_output = None


def calculate_indices(bands):
    # get specific bands
    if not bands:
        return
    for band in bands:
        if band.find("B08") != -1 or band.find("d05") != -1:
            nir_band = gdal.Open(band)
            nir_band = nir_band.ReadAsArray()
            # nir_band[nir_band == 0] = None --> how to get rid of invalid values?
        if band.find("B04") != -1 or band.find("d04") != -1:
            red_band = gdal.Open(band)
            red_band = red_band.ReadAsArray()
        if band.find("B02") != -1 or band.find("d02") != -1:
            blue_band = gdal.Open(band)
            blue_band = blue_band.ReadAsArray()
        if band.find("B12") != -1 or band.find("d07") != -1:
            swir_band = gdal.Open(band)
            swir_band = swir_band.ReadAsArray()
        if band.find("B03") != -1 or band.find("d03") != -1:
            green_band = gdal.Open(band)
            green_band = green_band.ReadAsArray()
        if band.find("B01") != -1 or band.find("d01") != -1:
            ca_band = gdal.Open(band)
            ca_band = ca_band.ReadAsArray()

    print(f'finished calculating indices for {bands[0]}')
    # calculate indices
    ndvi = calculate_ndvi(nir_band, red_band)
    evi = calculate_evi(nir_band, red_band, blue_band)
    gemi = calculate_gemi(nir_band, red_band)
    savi = calculate_savi(nir_band, red_band)

    path = bands[0][:-18] + ".hdfcloud_mask.tif"
    print(path)

    evi = applyCloudMask(ndvi, evi)
    gemi = applyCloudMask(ndvi, gemi)
    savi = applyCloudMask(ndvi, savi)

    # save indices img
    save_ind_img(bands[0][:-17], ndvi, "NDVI", bands[3])
    save_ind_img(bands[0][:-17], evi, "EVI", bands[3])
    save_ind_img(bands[0][:-17], gemi, "GEMI", bands[3])
    save_ind_img(bands[0][:-17], savi, "SAVI", bands[3])

def index_creation(path):
    if not path:
        return
    folder_path = path[:-3]
    bands_list = os.listdir(folder_path)
    band_paths = []
    for band in bands_list:
        band_path = os.path.join(folder_path, band)
        band_paths.append(band_path)
    calculate_indices(band_paths)
