import datetime

def extract_sensing_month(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        month = metadata[st_index + 18:st_index + 20]
        return int(month)


def extract_sensing_year(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        year = metadata[st_index + 13:st_index + 17]
        return int(year)


def extract_sensing_day(metadata):
    st_index = metadata.find("SENSING_TIME")
    if st_index != -1:
        day = metadata[st_index + 21:st_index + 23]
        return int(day)


def extract_sensing_date(metadata):
    year = extract_sensing_year(metadata)
    month = extract_sensing_month(metadata)
    day = extract_sensing_day(metadata)
    return datetime.datetime(year, month, day)

def extract_cloud_coverage(metadata):
    cc_index = metadata.find("cloud_coverage")
    if cc_index != -1:
        cloud_coverage = metadata[cc_index + 15:cc_index + 19]
        return int(cloud_coverage)


def extract_spatial_coverage(metadata):
    cc_index = metadata.find("spatial_coverage")
    if cc_index != -1:
        spatial_coverage = metadata[cc_index + 17:cc_index + 21]
        return int(spatial_coverage)