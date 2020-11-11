from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def sampling_k_elements(group, number_of_samples=10):
    if len(group) < number_of_samples:
        return group
    return group.sample(number_of_samples)


def plotSampleData(X, year, index, y, path):

    # Fix Y than concatenate
    dados = None
    dados = np.concatenate((X, y[:, None]), axis=1)

    # create columns
    col = ['Aug/2017', 'Sep/2017', 'Oct/2017', 'Nov/2017', 'Dec/2017', 'Jan/2018', 'Feb/2018', 'Mar/2018', 'Apr/2018',
           'May/2018', 'Jun/2018', 'Jul/2018', 'Class']
    # create dataframe
    df = pd.DataFrame(dados, columns=col)
    # Labels: 1 - Forest; 2- Pasture; 3 - Agriculture 4- Deforestation
    df['Class'] = df['Class'].replace(to_replace=[1, 2, 3, 4],
                                      value=["Forest", "Pasture", "Agriculture", "Deforestation"])

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
        plt.savefig(f"{path}ts{year}{index}_lineplot_randomsample_withNAN")


def createData(ts, path, index, year):
    '''
    Creates input Data for RF
    Input:
    ts: Array[] timeseries (3D array of index images)
    path: String path to folde
    index: String Index name
    year: Int Year for which to create data
    Output:
    X:sample data (pixel values)  y:labels of pixel
    '''
    # Read in our image and ROI image
    img_ds = ts
    roi_ds = gdal.Open(path + 'training_data_roi' + str(year) + '.tif', gdal.GA_ReadOnly)
    img = img_ds
    roi = roi_ds.GetRasterBand(1).ReadAsArray()

    # Find how many non-zero entries we have -- i.e. how many training data samples?
    n_samples = (roi > 0).sum()
    print('We have {n} samples'.format(n=n_samples))

    # What are our classification labels?
    labels = np.unique(roi[roi > 0])
    print('The training data include {n} classes: {classes}'.format(n=labels.size,
                                                                    classes=labels))
    print(f"The roi has a shape of {roi.shape} and the ts {img.shape}")
    # "X" matrix containing our features, "y" array containing our labels
    #     These will have n_samples rows

    X = img[roi > 0, :]  # .T  # map labels to coresponding pixels
    y = roi[roi > 0]

    plotSampleData(X, year, index, y, path)
    X = np.where(np.isnan(X), -9999, X)

    return X, y #    X:sample data (pixel values)  y:labels of pixel

