import os
import subprocess
import zipfile
import multiprocessing as mp

path = "/home/Usuario/Documents/sentinelHub"

dirList = os.listdir(path)
"""for folder in dirList:
    with zipfile.ZipFile(folder, 'r') as zip_ref:
        zip_ref.extractall(folder[:-4])
    #unzip file"""

filePathArray = []
for item in dirList:
    if not item.endswith(".zip"):
        path = os.path.join(item, path)
        for safeDir in os.listdir(path):
            safePath = os.path.join(path, safeDir)
            if os.path.isdir(safePath):
                for dir in os.listdir(safePath):
                    if dir == "GRANULE":
                        granulePath = os.path.join(safePath, dir)
                        for layerDir in os.listdir(granulePath):
                            filePath = os.path.join(granulePath, layerDir)
                            if os.path.isdir(filePath):
                                filePathArray.append(filePath)


def runFmask(pathToImage):
    print(pathToImage)
    #subprocess.check_output("Fmask_4_0 3 3 0 12", cwd=pathToImage)
    return subprocess.call("Fmask_4_0 2 2 2 12", cwd=pathToImage, shell=True)

print("starting Pool")
# Step 1: Init multiprocessing.Pool()
pool = mp.Pool(2)
# Step 2: `pool.map` the `runFmask`
result = pool.map(runFmask, filePathArray)

# Step 3: Don't forget to close
pool.close()
pool.join()
