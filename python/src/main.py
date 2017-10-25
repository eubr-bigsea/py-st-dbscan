# coding=UTF-8
#!/usr/bin/python

from datetime import datetime
import pandas as pd
import argparse
from stdbscan import *


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

    filename    = args.filename
    minPts      = args.minPts
    spatial_threshold   = args.spatial
    temporal_threshold  = args.temporal
    args = parser.parse_args()


    df = pd.read_csv(filename,sep=";",converters={'date_time': parse_dates})

    result = st_dbscan(df, spatial_threshold, temporal_threshold, minPts)
    print "Time Elapsed: {} seconds".format(time.time()-start)

    timestr = time.strftime("%Y%m%d-%H%M%S")

    output_name = "result_{}_{}_{}_{}.csv".format(spatial_threshold,
                                                  temporal_threshold,
                                                  minPts,
                                                  timestr)
    result.to_csv(output_name,index=False,sep=';')



if __name__ == "__main__":
    main()
