#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 12:00:09 2017

@author: Matthew
"""

from sklearn import cluster


def kmeans(data_list, clusters=5):
    kmeans = cluster.KMeans(n_clusters=clusters)
    kmean_data = kmeans.fit(data_list.tolist())

    centers = [(x[0], x[1]) for x in kmean_data.cluster_centers_]
    center_per_pt = kmean_data.labels_.tolist()

    cluster_data = {center: 0 for center in centers}
    for idx, centers in enumerate(centers):
        cluster_data[centers] = center_per_pt.count(idx)
    return cluster_data
