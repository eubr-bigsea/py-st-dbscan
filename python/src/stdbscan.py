from datetime import timedelta

import pyproj
'''
transfrom the lon and lat to x and y
'''
def p1_2_p2(df,p1_str = 'epsg:4326', p2_str = 'epsg:3395'):
    p1 = pyproj.Proj(init = p1_str)
    p2 = pyproj.Proj(init = p2_str)
    lon = df.longitude.values
    lat = df.latitude.values
    x1, y1 = p1(lon, lat)
    x2, y2 = pyproj.transform(p1, p2, x1, y1, radians=True)
    df['x'] = x2
    df['y'] = y2
    return df


def st_dbscan(df, spatial_threshold, temporal_threshold, min_neighbors):
    """
    Python st-dbscan implementation.
    INPUTS:
        df={o1,o2,...,on} Set of objects
        please make sure the first column is x, second is y, third is time
        
        spatial_threshold = Maximum geographical coordinate (spatial) distance
        value
        temporal_threshold = Maximum non-spatial distance value
        min_neighbors = Minimun number of points within Eps1 and Eps2 distance
    OUTPUT:
        C = {c1,c2,...,ck} Set of clusters
    """
    cluster_label = 0
    noise = -1
    unmarked = 777777
    stack = []

    # initialize each point with unmarked
    df['cluster'] = unmarked
    df['index'] = range(df.shape[0])
    m = df.values
    # for each point in database
    for index in range(m.shape[0]):
        if m[index, 3] == unmarked:
            neighborhood = retrieve_neighbors(index, m, spatial_threshold,
                                              temporal_threshold)

            if len(neighborhood) < min_neighbors:
                m[index, 3] = noise
            else:  # found a core point
                cluster_label += 1
                # assign a label to core point
                m[index,3] = cluster_label

                # assign core's label to its neighborhood
                for neig_index in neighborhood:
                    m[neig_index, 3] = cluster_label
                    stack.append(neig_index)  # append neighborhood to stack

                # find new neighbors from core point neighborhood
                while len(stack) > 0:
                    current_point_index = stack.pop()
                    new_neighborhood = retrieve_neighbors(
                        current_point_index, m, spatial_threshold,
                        temporal_threshold)

                    # current_point is a new core
                    if len(new_neighborhood) >= min_neighbors:
                        for neig_index in new_neighborhood:
                            neig_cluster = m[neig_index,3]
                            if any([neig_cluster == noise,
                                    neig_cluster == unmarked]):
                                m[neig_index,3] = cluster_label
                                stack.append(neig_index)
    return m


def retrieve_neighbors(index_center, m, spatial_threshold, temporal_threshold):
    neigborhood = []
    center_point = m[index_center,:]

    # filter by time
    min_time = center_point[2] - timedelta(seconds=temporal_threshold)
    max_time = center_point[2] + timedelta(seconds=temporal_threshold)
    m = m[(m[:,2] >= min_time) & (m[:,2] <= max_time),:]
    # filter by distance
    tmp = (m[:,0]-center_point[0])*(m[:,0]-center_point[0])+(m[:,1]-center_point[1])*(m[:,1]-center_point[1])
    neigborhood = m[tmp <= (spatial_threshold*spatial_threshold),4].tolist()
    neigborhood.remove(index_center)

    return neigborhood