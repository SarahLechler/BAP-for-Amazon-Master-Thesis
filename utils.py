from osgeo import gdal_array
import os
import datetime
import gdal

def extract_sensing_month(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        month = metadata[st_index + 18:st_index + 20]
        return int(month)


def extract_sensing_year(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        year = metadata[st_index + 13:st_index + 17]
        return int(year)


def extract_sensing_day(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        day = metadata[st_index + 21:st_index + 23]
        return int(day)


def extract_sensing_date(metadata):
    year = extract_sensing_year(metadata)
    month = extract_sensing_month(metadata)
    day = extract_sensing_day(metadata)
    return datetime.datetime(year, month, day)

def extract_sensing_date_from_filename(filename):
    year = extract_sensing_year_from_filename(filename)
    month = extract_sensing_month_from_filename(filename)
    day = extract_sensing_day_from_filename(filename)
    return datetime.datetime(year, month, day)

def extract_sensing_month_from_filename(filename):
    month = filename[-11:-9]
    return int(month)


def extract_sensing_year_from_filename(filename):
    return int(filename[-8:-4])


def extract_sensing_day_from_filename(filename):
    return int(filename[-14:-12])

def save_ind_img(path, array_img, name, tile, overwrite, metadata):
    month = extract_sensing_month(metadata)
    year = extract_sensing_year(metadata)
    day = extract_sensing_day(metadata)
    if month < 10:
        month = "0"+str(month)
    if day < 10:
        day = "0" + str(day)
    out_path = f"{path}/{name}d{day}m{month}y{year}.tif"
    if (os.path.isfile(out_path) and not overwrite):
        print(f"file {out_path} already exists")
        return
    ind_output = gdal_array.SaveArray(array_img, out_path, format="GTiff", prototype=f"../../../../scratch/tmp/s_lech05/hls_data/{tile}/template_file_{tile}.tif")
    print(f"saved file to {out_path}")
    daystring = extract_sensing_day_from_filename(out_path)
    monthstring = extract_sensing_month_from_filename(out_path)
    yearstring = extract_sensing_year_from_filename(out_path)
    print(f"day: {daystring}, month:{monthstring} year:{yearstring}")
    ind_output = None



""" 
    saved_image = gdal.Open(out_path, 1)
    if saved_image:
        saved_image.setMetadata(metadata)
        saved_image = None
driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(out_path, array_img.shape[0], array_img.shape[1], 1, gdal.GDT_Float32)
    dst_ds.SetMetadata(gdal.Info(template))
    outBand = dst_ds.GetRasterBand(1)
    outBand.WriteArray(array_img)
    outBand.FlushCache()
    georef = gdal.Open(f"../../../../scratch/tmp/s_lech05/hls_data/{tile}/template_file_{tile}.tif")
    proj = georef.GetProjection()
    transform = georef.GetGeoTransform()
    ref = georef.GetSpatialRef()
    dst_ds.setProjection(proj)
    dst_ds.SetGeoTransform(transform)
    dst_ds.SetSpatialRef(ref)
    print(f"saved file to {out_path}")"""


"""    
    ind_output = gdal_array.SaveArray(array_img, out_path, format="GTiff", prototype=template)
    print(f"saved file to {out_path}")
    ind_output = None
    saved_image = gdal.Open(out_path)
    saved_image = None
    if saved_image:
    ds = gdal.Open(out_path)
    print(metadata)
    print(ds)
    ds.setMetadata({'hello':'world'})
    ds = None"""



def extract_cloud_coverage(file_path):
    if file_path == None:
        return 100
    fileindex = file_path.find("v1.4/")
    metadata_file_path = file_path[:fileindex+4]+".h5"
    print(metadata_file_path)
    metadata = gdal.Info(metadata_file_path)
    cc_index = metadata.find("cloud_coverage")
    if cc_index != -1:
        cloud_coverage = metadata[cc_index + 15:cc_index + 19]
        return int(cloud_coverage)


def extract_spatial_coverage(file_path):
    if file_path == None:
        return 0
    fileindex = file_path.find("v1.4/")
    metadata_file_path = file_path[:fileindex+4]+".h5"
    metadata = gdal.Info(metadata_file_path)
    cc_index = metadata.find("spatial_coverage")
    if cc_index != -1:
        spatial_coverage = metadata[cc_index + 17:cc_index + 21]
        return int(spatial_coverage)
