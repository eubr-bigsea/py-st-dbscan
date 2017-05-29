#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import argparse
import time
import pandas as pd

from datetime import timedelta, datetime
from geopy.distance import great_circle

#COMPSs's imports
from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.functions.reduce import mergeReduce
from pycompss.functions.data import chunks


def getIndex(index,size_part):
    return index/size_part


def ST_DBSCAN(df,num_ids, spatial_threshold, temporal_threshold, min_neighbors,numFrag):
    cluster_label = 0
    NOISE = -999999
    UNMARKED = -1
    stack = []

    PartitionSize = int(math.ceil(float(num_ids)/numFrag))
    df = [d for d in chunks(df, PartitionSize )]

    Clusters = pd.DataFrame([UNMARKED] for i in range(num_ids))
    Clusters.columns = ['cluster']

    size_part = len(df[0])

    for ID_RECORD in xrange(1,num_ids):
        ID_PART = getIndex(ID_RECORD-1,size_part)
        CLUSTER = Clusters.loc[ID_RECORD-1]['cluster']

        if CLUSTER == UNMARKED:
            point = df[ID_PART].loc[ID_RECORD-1]
            ID_RECORD, DATATIME, LATITUDE, LONGITUDE = point

            X = retrieve_neighbors(point, df, spatial_threshold, temporal_threshold,numFrag)


            if len(X) < min_neighbors:
                Clusters.set_value(ID_RECORD-1, 'cluster', NOISE)
            else: # found a core point
                cluster_label += 1
                Clusters.set_value(ID_RECORD-1, 'cluster', cluster_label) # assign a label to core point

                for new_ID_RECORD in X: # assign core's label to its neighborhood
                    new_ID_RECORD = new_ID_RECORD[0]
                    Clusters.set_value(new_ID_RECORD-1, 'cluster', cluster_label)
                    if new_ID_RECORD not in stack:
                        stack.append(new_ID_RECORD) # append neighborhood to stack


                while len(stack) > 0: # find new neighbors from core point neighborhood
                    newest_ID_RECORD  = stack.pop()
                    newest_ID_PART = getIndex(newest_ID_RECORD-1,size_part)
                    new_point = df[newest_ID_PART].loc[newest_ID_RECORD-1]
                    Y = retrieve_neighbors(new_point,  df, spatial_threshold, temporal_threshold,numFrag)

                    if len(Y) >= min_neighbors: # current_point is a new core
                        for i in Y:
                            new_index_neig = i[0]
                            neig_cluster = Clusters.loc[new_index_neig-1]['cluster']
                            if (neig_cluster == UNMARKED):
                                Clusters.set_value(new_index_neig-1, 'cluster', cluster_label)
                                if new_index_neig not in stack:
                                    stack.append(new_index_neig)


    return Clusters


def retrieve_neighbors(point, df_parts, spatial_threshold, temporal_threshold, numFrag):
    partialResult = [[] for i in range(numFrag)]

    from pycompss.api.api import compss_wait_on
    for f in range(numFrag):
        partialResult[f] =  partial_neigborhood( df_parts[f], point, spatial_threshold, temporal_threshold )

    neigborhood   = mergeReduce(reduceTask, partialResult)
    neigborhood   = compss_wait_on(neigborhood,to_write=False)

    return neigborhood


@task(returns=list)
def partial_neigborhood( df_part, point, spatial_threshold, temporal_threshold):
    start=time.time()

    neigborhood = []
    ID_RECORD, DATATIME, LATITUDE, LONGITUDE = point


    min_time = DATATIME - timedelta(minutes = temporal_threshold)
    max_time = DATATIME + timedelta(minutes = temporal_threshold)

    for index, row in df_part.iterrows():
        # filter by time
        if  (row['DATATIME'] >= min_time) and (row['DATATIME'] <= max_time):
            if row['ID_RECORD'] != ID_RECORD:
                # filter by distance
                distance = great_circle((LATITUDE, LONGITUDE), (row['LATITUDE'], row['LONGITUDE'])).meters
                if distance <= spatial_threshold:
                    neigborhood.append([int(row['ID_RECORD'])])

    print "{}sec".format(time.time()-start)

    return neigborhood

@task(returns=list, priority=True)
def reduceTask(a, b):
    a = a + b
    return a


def parse_dates(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')

def main():

    parser = argparse.ArgumentParser(description='ST-DBSCAN  implementation with COMPSs')
    parser.add_argument('-f','--filename', help='Name of the file', required=True)
    args = parser.parse_args()

    filename = args.filename

    df = pd.read_csv(filename,sep=";",converters={'DATATIME': parse_dates})

    num_ids = len(df)
    print "Len:{}\n---".format(num_ids)

    numFrag = 4

    # STBSCAN
    spatial_threshold   = 500
    temporal_threshold  = 60
    minPts              = 5

    result_df = ST_DBSCAN(  df, num_ids, spatial_threshold,
                            temporal_threshold, minPts,numFrag)
    print "Finished"

    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    result_df['cluster'].to_csv("result_{}_{}_{}_{}.csv".format(spatial_threshold,
                                                                temporal_threshold,
                                                                minPts,
                                                                timestr)
                                                                )




if __name__ == "__main__":
    main()
