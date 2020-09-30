from osgeo import gdal_array
import os


def save_ind_img(path, array_img, name, template_file):
    out_path = path + name + '.tif'
    if (os.path.isfile(out_path)):
        return
    print(f"saved file to {out_path}")
    ind_output = gdal_array.SaveArray(array_img, out_path, format="GTiff", prototype=template_file)
    ind_output = None