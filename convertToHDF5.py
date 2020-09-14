import subprocess
import os
import multiprocessing as mp
import ranking


def convert_to_hdf5(hf4_path):
    print("translating file: "+hf4_path)
    subprocess.call(["./h4toh5.txt", hf4_path])


if __name__ == "__main__":
    file_paths = ranking.create_list_of_files()
    # STEP 1: create images in parallel
    #for file in list_of_files:
    print("starting Image Pool")
    pool = mp.Pool(4)
    result = pool.map(convert_to_hdf5, file_paths)
    pool.close()
    pool.join()
