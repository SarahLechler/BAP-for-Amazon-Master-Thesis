# Import Python 3's print function and division
from __future__ import print_function, division

# Import GDAL, NumPy, and matplotlib
from osgeo import gdal, gdal_array
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

def runRF(index, path, year, X, y, ts, tile, bap):
    '''
    Runs RF algorithm
    Input:
    index: String Name of index for which RF runs
    path: String Folder to save the result
    year: Int year for which RF runs
    X:sample data (pixel values)
    y:corresponding labels of pixel
    ts: timeseries (3D index array)
    bap: Boolean, BAP timeseries?
    Output:
    saves classification result to .tif file
    '''
    # Tell GDAL to throw Python exceptions, and register all drivers
    gdal.UseExceptions()
    gdal.AllRegister()
    img = np.asarray(ts)

    print('Creating classifier')
    # Initialize model with 500 trees
    rf = RandomForestClassifier(n_estimators=500, oob_score=True)

    # Fit model to training data
    rf = rf.fit(X, y)

    print('Our OOB prediction of for index {ind} accuracy is: {oob}%'.format(oob=rf.oob_score_ * 100, ind=index))

    print(img.shape[2])
    new_shape = (img.shape[0] * img.shape[1], img.shape[2])

    img_as_array = img.reshape(new_shape)
    print('Reshaped from {o} to {n}'.format(o=img.shape,
                                            n=img_as_array.shape))

    img_as_array = np.where(np.isnan(img_as_array), -9999, img_as_array.astype('float32'))
    img_as_array = np.where(np.isinf(img_as_array), -9999, img_as_array.astype('float32'))

    class_prediction = rf.predict(img_as_array)
    print(class_prediction.shape)
    #Labels: 1 - Forest; 2- Pasture; 3 - Agriculture 4- Deforestation
    class_prediction = class_prediction.reshape(img.shape[0], img.shape[1])
    # first_img = class_prediction[:, :, 0]
    if bap:
        out_path = path + 'classified_BAP' + index + str(year) + '.gtif'
    else:
        out_path = path + 'classified_Months' + index + str(year) + '.gtif'
    prediction_file = gdal_array.SaveArray(class_prediction, out_path, format="GTiff",
                                           prototype=path + "template_file_" + tile + '.tif')
    print(f"classified TS saved to {out_path}")
    prediction_file = None
    """  class_prediction = class_prediction.reshape(img[:, :, 0].shape)
    for image, i in range(class_prediction[3]):
        out_path = path + 'classified_' + index + i + '.gtif'
        prediction_file = gdal_array.SaveArray(image, out_path, format="GTiff", prototype=path + index + '.tif')
        prediction_file = None"""
