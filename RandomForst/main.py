
import multiprocessing as mp
from functools import partial
import matplotlib
matplotlib.use('Agg')

#own modules
import runDecisionTree
import runKMeans as km
import create_yearly_time_series as yts
import createInputData as cd
import runRandomForest
import createROIImage


def runOnIndices(index, year, tile):
    main_path = "../Images/21LYH/2018/L30/HLS.L30.T21LYH.2018019.v1.4/"
    #createROIImage.createROIImage(index, main_path, str(year))
    ts = yts.create_time_series(index, tile, [3660, 3660], year)
    data = cd.createData(ts, main_path, index, year)
    #km.runkmeans(data, year, index, tile)
    runRandomForest.runRF(index, main_path, year, data[0], data[1], ts)
    runDecisionTree.runDT(data[0], data[1], index)


if __name__ == "__main__":

    indices = ["NDVI", "SAVI", "GEMI", "EVI"]
    tiles = ['21LYH', '21LYG']
    years = [2018, 2017, 2016]
    inputs = [indices, tiles, years]
    pool = mp.Pool()

    result = pool.imap(partial(runOnIndices, year=2018, tile="21LYH"), indices)

    pool.close()
    pool.join()
    #    runOnIndices("NDVI", 2018, "21LYH")

