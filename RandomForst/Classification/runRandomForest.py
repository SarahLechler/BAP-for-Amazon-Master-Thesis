# Import Python 3's print function and division
from __future__ import print_function, division

# Import GDAL, NumPy, and matplotlib
from osgeo import gdal, gdal_array
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import create_yearly_time_series as yts


def runRF(index, path):
    # Tell GDAL to throw Python exceptions, and register all drivers
    gdal.UseExceptions()
    gdal.AllRegister()

    # Read in our image and ROI image
    img_ds = np.asarray(yts.create_time_series(index, "21LYH", [3660, 3660]))
    """ gdal.Open(path+index+'.tif', gdal.GA_ReadOnly)"""
    roi_ds = gdal.Open(path + 'training_data' + index + '.gtif', gdal.GA_ReadOnly)
    img = img_ds
    """np.zeros_like(img_ds)
    for b in range(img.shape[2]):
        img[:, :, b] = img_ds[:, :, b]"""
    # TODO: control the roi raster (really small) --> maybe try out different year?
    roi = roi_ds.GetRasterBand(1).ReadAsArray()

    # Find how many non-zero entries we have -- i.e. how many training data samples?
    n_samples = (roi > 0).sum()
    print('We have {n} samples'.format(n=n_samples))

    # What are our classification labels?
    labels = np.unique(roi[roi > 0])
    print('The training data include {n} classes: {classes}'.format(n=labels.size,
                                                                    classes=labels))
    # We will need a "X" matrix containing our features, and a "y" array containing our labels
    #     These will have n_samples rows
    #     In other languages we would need to allocate these and them loop to fill them, but NumPy can be faster

    X = img[roi > 0, :] # .T  # map labels to coresponding pixels
    y = roi[roi > 0]
   # y = y.reshape(y.shape[0], 1)
    X = np.where(np.isnan(X), -999, X)

    """for image in X:
        xnan = np.isnan(image)
        classes = np.unique(xnan)
        for c in classes:
            if c and (xnan == c).sum() >= image.shape[0]/2:
    """
    print(X.shape)
    print(y.shape)
    # Mask out clouds, cloud shadows, and snow using Fmask
    # TODO: reshape X and Y to the same size
    """
    for image in range(0, nan):
        X[image] = X[image, ~nan[image]]"""
    """ X_y = np.concatenate((X, y), axis=0)
    print(X_y)

    X_y = X_y[:, ~np.isnan(X_y).any(axis=0)]
    print(X_y)
    X = np.hsplit(X_y, [-1])[0]
    print(X)
    y = np.hsplit(X_y, [-1])[1].ravel()
    print(y)"""

    print('Creating classifier')
    # Initialize our model with 500 trees
    rf = RandomForestClassifier(n_estimators=500, oob_score=True)

    # Fit our model to training data
    rf = rf.fit(X, y)

    print('Our OOB prediction of for index {ind} accuracy is: {oob}%'.format(oob=rf.oob_score_ * 100, ind=index))

    # Take our full image, ignore the Fmask band, and reshape into long 2d array (nrow * ncol, nband) for classification
    new_shape = (img.shape[0] * img.shape[1], img.shape[2])

    img_as_array = img.reshape(new_shape)
    print('Reshaped from {o} to {n}'.format(o=img.shape,
                                            n=img_as_array.shape))

    img_as_array = np.where(np.isnan(img_as_array), -999, img_as_array.astype('float32'))
    img_as_array = np.where(np.isinf(img_as_array), -999, img_as_array.astype('float32'))

    class_prediction = rf.predict(img_as_array)
    print(class_prediction.shape)
    class_prediction = class_prediction.reshape(img.shape[0], img.shape[1])
    #first_img = class_prediction[:, :, 0]
    out_path = path + 'classified_' + index + '.gtif'
    prediction_file = gdal_array.SaveArray(class_prediction, out_path, format="GTiff", prototype=path + index + '.tif')
    prediction_file = None
    """  class_prediction = class_prediction.reshape(img[:, :, 0].shape)
    for image, i in range(class_prediction[3]):
        out_path = path + 'classified_' + index + i + '.gtif'
        prediction_file = gdal_array.SaveArray(image, out_path, format="GTiff", prototype=path + index + '.tif')
        prediction_file = None"""
