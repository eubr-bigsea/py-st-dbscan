# coding=UTF-8
#!/usr/bin/python

from datetime import datetime
import pandas as pd
import argparse
from stdbscan import *
import numpy as np

"""
    The minimal command to run this algorithm is:
    $ python main.py -f sample.csv

    Or could be executed with advanced configurations:
    $ python main.py -f sample.csv -p 5 -s 500 -t 60

    In the current momment, the dataset must have the
    'latitude', 'longitude' and 'date_time' columns, but
    if you want, can be easily changed.

"""

def parse_dates(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')


def plot_clusters(df, output_name):
    import matplotlib.pyplot as plt

    labels = df['cluster'].values
    X = df[['longitude','latitude']].values

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
    #plt.show()
    plt.savefig(output_name)


def main():
    import time
    start= time.time()
    parser = argparse.ArgumentParser(description='ST-DBSCAN in Python')
    parser.add_argument('-f','--filename', help='Name of the file', required=True)
    parser.add_argument('-p','--minPts',   help='Minimum number of points', required=False, type=int, default=15)
    parser.add_argument('-s','--spatial',  help='Spatial Threshold (in meters)', required=False, type=float, default=500)
    parser.add_argument('-t','--temporal', help='Temporal Threshold (in seconds)', required=False, type=float, default=60)
    args = parser.parse_args()
    args = parser.parse_args()

    filename = args.filename
    min_points = args.minPts
    spatial_threshold = args.spatial
    temporal_threshold = args.temporal
    args = parser.parse_args()

    df = pd.read_csv(filename,sep=";",converters={'date_time': parse_dates})

    result = st_dbscan(df, spatial_threshold, temporal_threshold, min_points)
    print "Time Elapsed: {} seconds".format(time.time()-start)

    timestr = time.strftime("%Y%m%d-%H%M%S")

    output_name = "result_{}_{}_{}_{}".format(spatial_threshold,
                                                  temporal_threshold,
                                                  min_points,
                                                  timestr)
    result.to_csv(output_name+'.csv',index=False,sep=';')

    plot_clusters(df, output_name+'.png')

    df = df[df.cluster != -1]
    print df.groupby('cluster').agg({'latitude': ['min', 'max'],
                                     'longitude': ['min', 'max'],
                                     'date_time': ['min', 'max']})



if __name__ == "__main__":
    main()
