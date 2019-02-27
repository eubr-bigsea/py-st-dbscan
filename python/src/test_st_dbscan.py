from datetime import datetime
import pandas as pd

from stdbscan import st_dbscan, p1_2_p2

def parse_dates(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')

filename = 'sample.csv'


def test_time():
    df = pd.read_csv(filename,sep=";",converters={'date_time': parse_dates})
    '''
    transfrom the lon and lat to x and y
    need to selcet the right epsg
    I don't the true epsg of sample, but get the same result by using epsg:4326 and epsg:32635
    '''
    df = p1_2_p2(df,p1_str = 'epsg:4326', p2_str = 'epsg:32635')
    df_to_cluster = df[['x', 'y', 'date_time']]
    result_t600 = st_dbscan(df_to_cluster.copy(), spatial_threshold=500, temporal_threshold=600, min_neighbors=5)
    return result_t600

if __name__ == '__main__':
    df = pd.DataFrame(test_time())
    print(pd.value_counts(df[3]))