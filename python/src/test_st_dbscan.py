from datetime import datetime
import pandas as pd
import numpy as np
from stdbscan import STDBSCAN


def parse_dates(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')


def plot_clusters(df, output_name):
    import matplotlib.pyplot as plt

    labels = df['cluster'].values
    X = df[['longitude', 'latitude']].values

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        xy = X[class_member_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=6)

    plt.title('ST-DSCAN: #n of clusters {}'.format(len(unique_labels)))
    plt.show()
    # plt.savefig(output_name)


def test_time():
    filename = 'sample.csv'
    df = pd.read_csv(filename, sep=";", converters={'date_time': parse_dates})
    '''
    transfrom the lon and lat to x and y
    need to select the right epsg
    I don't the true epsg of sample, but get the same result by using 
    epsg:4326 and epsg:32635
    '''
    st_dbscan = STDBSCAN(col_lat='latitude', col_lon='longitude',
                         col_time='date_time', spatial_threshold=500,
                         temporal_threshold=600, min_neighbors=5)
    df = st_dbscan.projection(df, p1_str='epsg:4326', p2_str='epsg:32635')
    result_t600 = st_dbscan.run(df)
    return result_t600


if __name__ == '__main__':
    df = pd.DataFrame(test_time())
    print(pd.value_counts(df['cluster']))
