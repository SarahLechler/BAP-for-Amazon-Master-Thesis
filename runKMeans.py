import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs


def initkMeans(time_series, year, index, tile):
    y_pred = KMeans(n_clusters=4,
                    random_state=0).fit_predict(time_series)
    plt.figure(figsize=(12, 12))

    plt.subplot(224)
    plt.scatter(time_series[:, 0], time_series[:, 1], c=y_pred)
    plt.title(f"KMeans for tile {tile} and year: {year} and index {index}")

    plt.savefig(f'../Images/plots/kmeans {tile}{year}{index}')
    return y_pred


def plotKMeans(kmeans, time_series, year, index, tile):
    plt.figure(figsize=(12, 12))

    plt.scatter(time_series[:, 0], time_series[:, 1], c=kmeans)
    plt.title(f"KMeans for tile {tile} and year: {year} and index {index}")
    plt.savefig(f'../Images/plots/kmeans {tile}{year}{index}')


def runkmeans(time_series, year, index, tile):
    kmeans = initkMeans(time_series[0], year, index, tile)
    #plotKMeans(kmeans, time_series[0], year, index, tile)
