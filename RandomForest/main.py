
import multiprocessing as mp
from functools import partial
import matplotlib
matplotlib.use('Agg')

#own modules
#import RandomForest.runDecisionTree as rundt
#import runKMeans as km
import RandomForest.create_yearly_time_series as yts
#import RandomForest.createInputData as cd
#import RandomForest.runRandomForest as rf
#import RandomForest.createROIImage as roi


def runOnIndices(index, year, tile, path):
    main_path = path
    #createROIImage.createROIImage(index, main_path, str(year))
    ts = yts.create_time_series(index, tile, year, True)
    #data = cd.createData(ts, main_path, index, year)
    #km.runkmeans(data, year, index, tile)
    #rf.runRF(index, main_path, year, data[0], data[1], ts)
    #rundt.runDT(data[0], data[1], index)


if __name__ == "__main__":

    indices = ["NDVI", "SAVI", "GEMI", "EVI"]
    tiles = ['21LYH', '21LYG']
    years = [2018, 2017, 2016]
    inputs = [indices, tiles, years]
    pool = mp.Pool()

    result = pool.imap(partial(runOnIndices, year=2018, tile="21LYH", path="../../../../scratch/tmp/s_lech05/hls_data/21LYH/2018/L30/HLS.L30.T21LYH.2018019.v1.4/"), indices)

    pool.close()
    pool.join()
    #    runOnIndices("NDVI", 2018, "21