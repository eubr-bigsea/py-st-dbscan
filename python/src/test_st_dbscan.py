#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pandas as pd
import numpy as np
from stdbscan import STDBSCAN
from coordinates import convert_to_utm


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
    First, we transform the lon/lat (geographic coordinates) to x and y 
    (in meters), in order to this, we need to select the right epsg (it 
    depends on the trace). After that, we run the algorithm. 
    '''
    st_dbscan = STDBSCAN(spatial_threshold=500, temporal_threshold=600,
                         min_neighbors=5)

    df = convert_to_utm(df, src_epsg=4326, dst_epsg=32633,
                        col_lat='latitude', col_lon='longitude')

    result_t600 = st_dbscan.fit_transform(df, col_lat='latitude',
                                          col_lon='longitude',
                                          col_time='date_time')
    return result_t600


if __name__ == '__main__':
    df = pd.DataFrame(test_time())
    print(pd.value_counts(df['cluster']))
