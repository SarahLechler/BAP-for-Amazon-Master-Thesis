import os
import numpy
from datetime import datetime
import copy

from bfast import BFASTMonitor
from bfast.utils import crop_data_dates
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


def run_bfast(indice_array):
    '''
    Runs BFAST algorithm
    Input:
    indice_array: Array[] sorted 3D array with image arrays for the whole period
    Output:
    Breaks and mean of timeseries
    '''
    print("starting Bfast Process")
    # set parameters
    k = 3
    freq = 30
    trend = True
    hfrac = 0.25
    level = 0.05
    start_hist = datetime(2013, 8, 1)  # set start of history period
    start_monitor = datetime(2019, 7, 1)  # set start of monitoring perios
    end_monitor = datetime(2020, 7, 31)  # set end of monitoring period

    dates = pd.date_range('2013-08-01', '2020-07-31', freq='MS')  # create data array
    dates2 = [pd.to_datetime(date) for date in dates]
    nancount = numpy.count_nonzero(numpy.isnan(indice_array))
    print(f"Timeseries has {nancount} NANs")
    indice_array = numpy.where(numpy.isnan(indice_array), -9999, indice_array)  # supstitute noData values
    indice_array = indice_array * 10000
    indice_array = indice_array.astype(int)
    data, dates = crop_data_dates(indice_array, dates2, start_hist, end_monitor)  # crop array

    while len(dates2) > data.shape[0]:
        dates2.pop()
    if len(dates2) < data.shape[0]:
        dates2.insert(0, datetime(2013, 1, 1))

    print("First date: {}".format(dates2[0]))
    print("Last date: {}".format(dates2[-1]))
    print("Shape of data array: {}".format(data.shape))
    print(f'Number of dates {len(dates2)}')

    # create BFAST model
    model = BFASTMonitor(
        start_monitor,
        freq=freq,
        k=k,
        hfrac=hfrac,
        trend=trend,
        level=level,
        backend='python',
        verbose=1
    )
    # data = data[:, 2330:3000, :]
    model.fit(data, dates, n_chunks=5, nan_value=-9999)  # fit model to timeseries
    # bfastSingle.fit_single(data, dates2, model)

    # save results
    breaks = model.breaks
    means = model.means

    return breaks, means  # return detected breaks in timeseries and mean values of pixel


"""
    no_breaks_indices = (breaks == -1)
    means[no_breaks_indices] = 0
    means[means > 0] = 0
    breaks_plot = breaks.astype(numpy.float)
    breaks_plot[breaks == -2] = numpy.nan
    breaks_plot[breaks == -1] = numpy.nan
    breaks_plot[means >= 0] = numpy.nan

    dates_monitor = []

    # collect dates for monitor period
    for i in range(len(dates)):
        if start_monitor <= dates[i]:
            dates_monitor.append(dates[i])
    dates_array = numpy.array(dates_monitor)
    idx_start_2018 = numpy.argmax((dates_array >= datetime(2018, 1, 1)) > False)

    breaks_plot_years = copy.deepcopy(breaks_plot)
    breaks_plot_years[breaks_plot <= idx_start_2018] = 0

    cmap = plt.get_cmap("gist_rainbow")
    cmaplist = [cmap(i) for i in range(cmap.N)]
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    bounds = numpy.linspace(0, 6, 7)
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    im = axes.imshow(breaks_plot_years, cmap=cmap, vmin=0, vmax=6, norm=norm)
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax, ticks=[0, 1, 2, 3, 4, 5, 6])
    labels = cbar_ax.set_yticklabels(['2018'])

    plt.show()"""
