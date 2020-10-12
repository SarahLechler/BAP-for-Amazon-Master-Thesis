import nasa_hls

def filter_data(df_datasets):
    df_datasets["year"] = df_datasets.date.dt.year
    df_datasets["month"] = df_datasets.date.dt.month
    df_datasets["day"] = df_datasets.date.dt.day

    ls_s2_aquisitions_same_day = df_datasets.duplicated(subset=["tile", "year", "month", "day"], keep=False)

    df_download = df_datasets[(ls_s2_aquisitions_same_day) & \
                              # (df_datasets["tile"] == "32UNU") & \
                              (df_datasets["date"].dt.year == 2019) & \
                              (df_datasets["date"].dt.month == 4)]
    df_download = df_download.sort_values(["date", "tile", "product"])
    print("Number of datasets after filtering: ", df_download.shape[0])

    return df_download


def download_data(data_def, tile, year, product):
    nasa_hls.download_batch(dstdir="./hls_downloads/" + tile + "/" + year + "/" + product,
                            datasets=data_def,
                            version="v1.4",
                            overwrite=False)

    data_def["id"] = data_def["url"].str.split("/", expand=True)[11].str[0:-4]
    print(data_def)
    data_def["path"] = "./hls_dataset/" #"../../../../scratch/tmp/s_lech05/hls_data/" + tile + "/" + year + "/" + product + "/" + data_def["id"] + ".hdf"
    data_def


if __name__ == '__main__':
    years = [2017,2018,2019] #2013, 2014, 2015,2016, 2020
    products = ["L30", "S30"]
    tiles = ["21LYG", "21LYH"]
    for year in years:
        for product in products:
            if (year == 2013 or year == 2014) and product == 'S30':
                continue
            else:
                for tile in tiles:
                    df_datasets = nasa_hls.get_available_datasets(products=[product],  # , "S30"],
                                                                  years=[year],
                                                                  # , 2014, 2015, 2016, 2017, 2018, 2019, 2020],
                                                                  tiles=[tile],
                                                                  return_list=False)
                    print("Number of datasets: ", df_datasets.shape[0])
                    # filteredData = filter_data(df_datasets)
                    download_data(df_datasets, tile, str(year), product)

    """df_datasets = nasa_hls.get_available_datasets(products=["L30", "S30"],
                                                  years=[2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
                                                  tiles=["21LYH", "21LYG"],
                                                  return_list=False)
    print("Number of datasets: ", df_datasets.shape[0])
    # filteredData = filter_data(df_datasets)
    download_data(df_datasets)
"""