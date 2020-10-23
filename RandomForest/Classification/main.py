import runRandomForest
import createROIImage
import multiprocessing as mp

def runOnIndices(index):
    main_path = "../Images/21LYH/2018/L30/HLS.L30.T21LYH.2018019.v1.4/"
    #createROIImage.createROIImage(index, main_path)
    runRandomForest.runRF(index, main_path)


if __name__ == "__main__":
    runOnIndices("NDVI")
"""    indices = ["NDVI", "SAVI", "GEMI", "EVI", "RNDSI"]

    pool = mp.Pool()

    result = pool.map(runOnIndices, indices)

    pool.close()
    pool.join()
"""