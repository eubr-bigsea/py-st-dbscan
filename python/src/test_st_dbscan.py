from datetime import datetime
import pandas as pd
import argparse
from stdbscan import st_dbscan

def parse_dates(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')

filename = 'sample.csv'


def test_time():
    df = pd.read_csv(filename,sep=";",converters={'date_time': parse_dates})
    result_t600 = st_dbscan(df, spatial_threshold=500, temporal_threshold=600, min_neighbors=5)

    df = pd.read_csv(filename,sep=";",converters={'date_time': parse_dates})
    result_t6 = st_dbscan(df, spatial_threshold=500, temporal_threshold=0.6, min_neighbors=5)

    assert not result_t600.equals(result_t6)


if __name__ == '__main__':
    test_time()
