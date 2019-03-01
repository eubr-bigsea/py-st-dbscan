#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import timedelta
import pyproj


class STDBSCAN(object):

    def __init__(self, col_lat, col_lon, col_time, spatial_threshold=500.0, 
                 temporal_threshold=60.0, min_neighbors=15):
        """
        Python st-dbscan implementation.

        :param col_lat: Latitude column name;
        :param col_lon:  Longitude column name;
        :param col_time: Date time column name;
        :param spatial_threshold: Maximum geographical coordinate (spatial)
             distance value;
        :param temporal_threshold: Maximum non-spatial distance value (meters);
        :param min_neighbors: Minimum number of points within Eps1 and Eps2
             distance;
        """
        self.col_lat = col_lat
        self.col_lon = col_lon
        self.col_time = col_time
        self.spatial_threshold = spatial_threshold
        self.temporal_threshold = temporal_threshold
        self.min_neighbors = min_neighbors

    def projection(self, df, p1_str='epsg:4326', p2_str='epsg:3395'):
        """
        Cython wrapper to converts from geographic (longitude,latitude)
        to native map projection (x,y) coordinates. It needs to select the
        right epsg. Values of x and y are given in meters
        """
        p1 = pyproj.Proj(init=p1_str)
        p2 = pyproj.Proj(init=p2_str)
        lon = df[self.col_lon].values
        lat = df[self.col_lat].values
        x1, y1 = p1(lon, lat)
        x2, y2 = pyproj.transform(p1, p2, x1, y1, radians=True)
        df[self.col_lon] = x2
        df[self.col_lat] = y2

        print df
        return df

    def _retrieve_neighbors(self, index_center, matrix):

        center_point = matrix[index_center, :]

        # filter by time
        min_time = center_point[2] - timedelta(seconds=self.temporal_threshold)
        max_time = center_point[2] + timedelta(seconds=self.temporal_threshold)
        matrix = matrix[(matrix[:, 2] >= min_time) &
                        (matrix[:, 2] <= max_time), :]
        # filter by distance
        tmp = (matrix[:, 0]-center_point[0])*(matrix[:, 0]-center_point[0]) + \
            (matrix[:, 1]-center_point[1])*(matrix[:, 1]-center_point[1])
        neigborhood = matrix[tmp <= (
            self.spatial_threshold*self.spatial_threshold), 4].tolist()
        neigborhood.remove(index_center)

        return neigborhood

    def run(self, df):
        """
        INPUTS:
            df={o1,o2,...,on} Set of objects;

        OUTPUT:
            C = {c1,c2,...,ck} Set of clusters
        """
        cluster_label = 0
        noise = -1
        unmarked = 777777
        stack = []

        # initial setup
        df = df[[self.col_lon, self.col_lat, self.col_time]]
        df = df.assign(cluster=unmarked)
        df['index'] = range(df.shape[0])
        matrix = df.values
        df.drop(['index'], inplace=True, axis=1)

        # for each point in database
        for index in range(matrix.shape[0]):
            if matrix[index, 3] == unmarked:
                neighborhood = self._retrieve_neighbors(index, matrix)

                if len(neighborhood) < self.min_neighbors:
                    matrix[index, 3] = noise
                else:  # found a core point
                    cluster_label += 1
                    # assign a label to core point
                    matrix[index, 3] = cluster_label

                    # assign core's label to its neighborhood
                    for neig_index in neighborhood:
                        matrix[neig_index, 3] = cluster_label
                        stack.append(neig_index)  # append neighbors to stack

                    # find new neighbors from core point neighborhood
                    while len(stack) > 0:
                        current_point_index = stack.pop()
                        new_neighborhood = \
                            self._retrieve_neighbors(current_point_index,
                                                     matrix)

                        # current_point is a new core
                        if len(new_neighborhood) >= self.min_neighbors:
                            for neig_index in new_neighborhood:
                                neig_cluster = matrix[neig_index, 3]
                                if any([neig_cluster == noise,
                                        neig_cluster == unmarked]):
                                    matrix[neig_index, 3] = cluster_label
                                    stack.append(neig_index)

        df['cluster'] = matrix[:, 3]
        return df

