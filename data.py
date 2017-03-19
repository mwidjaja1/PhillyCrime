# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import datetime as dt
import geoplot
import learn
import os
import pandas as pd
import pickle
import sqlite3


def load_csv(path):
    """ Loads the Crime.csv Pandas CSV  """
    cols = ['Dc_Dist', 'Psa', 'Dispatch_Date_Time', 'Dispatch_Date',
            'Dispatch_Time', 'Hour', 'Dc_Key', 'Location_Block', 'UCR_General',
            'Text_General_Code',  'Police_Districts', 'Month', 'Lon', 'Lat']
    col_types = {'Dc_Dist': str, 'Psa': str, 'Dispatch_Date_Time': str,
                 'Dispatch_Date': str, 'Dispatch_Time': str, 'Hour': str,
                 'Dc_Key': str, 'Location_Block': str, 'UCR_General': str,
                 'Text_General_Code': str, 'Police_Districts': str,
                 'Month': str, 'Lon': float, 'Lat': float}
    data_orig = pd.read_csv('crime.csv', header=0, names=cols, dtype=col_types,
                            parse_dates=[2], infer_datetime_format=True)
    return prepare_data(data_orig)


def prepare_data(data):
    """ Modifies the original data set from the CSV File """
    data['Month'] = data['Month'].apply(lambda x:
                                        dt.datetime.strptime(x, '%Y-%m'))
    data['Text_General_Code'] = data['Text_General_Code'].fillna('Unknown')

    # To-Do: Actually deal with locations without coordinates
    data = data[data['Lat'].isnull() == False]
    return data


def creates_clusters(data, col='coordinate', name='crime', clusters=5):
    """ Creates a K-Means Cluster with the given data points.

        Inputs:
        data: The DataFrame to create clusters from
        col: The column within the DataFrame to analyze in particular.
             For this data set, this should be tuple-able coordinates
        name: The text part for the pickled file's name, which pickled center.
        clusters: The qty of clusters to produce

        Outputs:
        center: A dict with each cluster's coordinate center and how many
                occurances happened in each cluster.
    """
    center_pickle_name = '{}_{}.pkl'.format(name, clusters)
    try:
        if os.path.isfile(center_pickle_name):
            print('Opening up {}'.format(center_pickle_name))
            centers = pickle.load(open(center_pickle_name, 'rb'))
        else:
            print('Clustering data & creating {}'.format(center_pickle_name))
            centers = learn.kmeans(data[col], clusters)
            pickle.dump(centers, open(center_pickle_name, 'wb'))
    except Exception as err:
        print('ERROR: Cannot cluster data[{}] with {} clusters'
              .format(col, clusters))
        print(err)
    return centers


def sum_of_crimes(data, lon_col='Lon', lat_col='Lat'):
    """ Takes a DataFrame of crimes & sums crimes up by rounded coordinates.

        Inputs:
        data: DataFrame of crimes
        lon_col = What column to use for the longitude [default = 'lon']
        lat_col = What column to use for the latitude [default = 'lat']
    """
    data['lat_short'], data['lon_short'], data['coordinate'] =\
        simplify_coordinate(data['Lon'], data['Lat'])
    crimes_by_coordinate = data.groupby(by='coordinate').size()
    return crimes_by_coordinate


def simplify_coordinate(lon, lat):
    """ Combines coordinates into a tuple, after rounding them down """
    longitude = lon.round(5)  # round(lon*4)/4
    latitude = lat.round(5)  # round(lat*4)/4
    # coordinates = [(x[0], x[1]) for x in zip(latitude, longitude)]
    coordinates = [(x[0], x[1]) for x in zip(lat, lon)]
    return latitude, longitude, coordinates


def main():
    """ Main Function """
    # Import CSV if a Db file is not present, otherwise, open the db
    if not os.path.isfile('crime.pkl') and not os.path.isfile('crime.db'):
        print('Loading crime.csv')
        data = load_csv('crime.csv')
        conn = sqlite3.connect('crime.db')
    elif os.path.isfile('crime.db'):
        print('Loading crime.db')
        conn = sqlite3.connect('crime.db')
        data = pd.read_sql_query('SELECT * FROM Crime;', conn)
    else:
        print('Loading crime.pkl')
        data = pd.read_pickle('crime.pkl')

    # Creates Coordinates
    print('Creating Coordinates')
    data['coordinate'] = [(x[0], x[1]) for x in zip(data['Lat'], data['Lon'])]

    # Clusters & Plots All Crimes
    centers = creates_clusters(data, name='crime_all', clusters=20)
    map_opts = {'lat': 39.992003865395425, 'lng': -75.14991150054124,
                'size': .00005, 'color': '#3186cc'}
    print('Plots All Crimes')
    geoplot.scatterplot_map(centers, map_opts, "crime_all.html")

    # Filters Crimes by Severity
    # Credit: http://gis.chicagopolice.org/CLEARMap_crime_sums/crime_types.html
    index_crimes = ['Thefts', 'Arson', 'Theft from Vehicle',
                    'Robbery No Firearm', 'Robbery Firearm',
                    'Motor Vehicle Theft', 'Rape', 'Burglary Residential',
                    'Homicide - Criminal', 'Aggravated Assault No Firearm',
                    'Aggravated Assault Firearm', 'Burglary Non-Residential',
                    'Recovered Stolen Motor Vehicle']
    data_index = data[data['Text_General_Code'].isin(index_crimes)]
    data_not_index = data[~data['Text_General_Code'].isin(index_crimes)]

    # Clusters & Plots Crimes by Severity
    map_opts = {'lat': 39.992003865395425, 'lng': -75.14991150054124,
                'size': .0002, 'color': '#3186cc'}
    centers_idx = creates_clusters(data_index, name='crime_idx', clusters=15)
    print('Plots Index Crimes')
    geoplot.scatterplot_map(centers_idx, map_opts, "crime_idx.html")

    centers_not_idx = creates_clusters(data_not_index, name='crime_not_idx',
                                       clusters=15)
    print('Plots Not-Index Crimes')
    geoplot.scatterplot_map(centers_not_idx, map_opts, "crime_not_idx.html")


    """
    # Rounds Coordinates
    print('Summarizes Data')
    crimes_all = sum_of_crimes(data)

    # Plots all crimes
    map_opts = {'lat': 39.992003865395425,
                'lng': -75.14991150054124,
                'size': 1,
                'color': '#3186cc'}
    print('Creating All Crimes Plot')
    geoplot.scatterplot_map(crimes_all, map_opts, "crime_all.html")

    # Saves Pickle File
    # data.to_pickle('crime.pkl')

    # Saves SQL Database
    #print('Creating Database')
    if 'coordinate' in data.columns:
        del data['coordinate']
    data.to_sql('Crime', conn, if_exists='replace', chunksize=1000)
    conn.close()
    """

    return data, centers


if __name__ == "__main__":
    data, centers = main()
