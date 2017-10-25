# coding=UTF-8
#!/usr/bin/python

from datetime import datetime
import pandas as pd
import argparse
from stdbscan import *


def parse_dates(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')

def main():
    import time
    start= time.time()
    parser = argparse.ArgumentParser(description='ST-DBSCAN  implementation with COMPSs')
    parser.add_argument('-f','--filename', help='Name of the file', required=True)
    args = parser.parse_args()

    filename = args.filename
    df = pd.read_csv(filename,sep=";",converters={'DATATIME': parse_dates})

    spatial_threshold   = 500   #in meters
    temporal_threshold  = 60    #in seconds
    minPts              = 5

    
    result = ST_DBSCAN(df,numPoints, spatial_threshold, temporal_threshold, minPts)
    print "Time Elapsed: {} seconds".format(time.time()-start)

    timestr = time.strftime("%Y%m%d-%H%M%S")

    result_df.to_csv("result_{}_{}_{}_{}.csv".format(spatial_threshold,temporal_threshold,minPts,timestr))



if __name__ == "__main__":
    main()
