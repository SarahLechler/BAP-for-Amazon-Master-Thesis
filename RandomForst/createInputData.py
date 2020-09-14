from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def sampling_k_elements(group, number_of_samples=10):
    if len(group) < number_of_samples:
        return group
    return group.sample(number_of_samples)


def plotSampleData(X, year, index, y):

    # Fix Y than concatenate
    dados = None
    dados = np.concatenate((X, y[:, None]), axis=1)

    # create columns
    col = ['Aug/2017', 'Sep/2017', 'Oct/2017', 'Nov/2017', 'Dec/2017', 'Jan/2018', 'Feb/2018', 'Mar/2018', 'Apr/2018',
           'May/2018', 'Jun/2018', 'Jul/2018', 'Class']
    # create dataframe
    df = pd.DataFrame(dados, columns=col)
    # replace labels
    df['Class'] = df['Class'].replace(to_replace=[1, 2, 3, 4],
                                      value=["Agriculture", "Pasture", "Forest", "Deforestation"])

    """balanced = df.groupby('Class').apply(sampling_k_elements).drop('Class', axis=1).reset_index().drop('level_1',
                                                                                                       axis=1)"""
    df = df.dropna()
    df = df.reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(13, 7))
    print(df["Class"].value_counts())
    for i, m in df.groupby('Class'):
        t = np.arange(len(m.mean()) - 1)
        ax.plot(m.mean(), label=i)
        #legend = ax.legend(loc='upper left', shadow=True, fontsize='large', ncol=4)
        plt.title(f"TS for year: {year} and index {index}")
        plt.ylabel(f'{index} value')
        plt.xlabel('Month of Prodes Year')
        plt.savefig(f'../hls_data/plots/ts{year}{index}_lineplot_randomsample_withNAN')


def createData(ts, path, index, year):
    # Read in our image and ROI image
    img_ds = ts
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

    X = img[roi > 0, :]  # .T  # map labels to coresponding pixels
    y = roi[roi > 0]

    plotSampleData(X, year, index, y)
    X = np.where(np.isnan(X), -999, X)

    return X, y
