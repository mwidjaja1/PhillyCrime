# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from bokeh.models import ColumnDataSource, GMapOptions
import datetime as dt
import geoplot
import os
import pandas as pd
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


def sum_of_crimes(data, lon_col='Lon', lat_col='Lat'):
    """ Takes a DataFrame of crimes & sums crimes up by rounded coordinates.

        Inputs:
        data: DataFrame of crimes
        lon_col = What column to use for the longitude [default = 'lon']
        lat_col = What column to use for the latitude [default = 'lat']
    """
    if 'coordinate' not in data.columns:
        data['lon_short'], data['lat_short'], data['coordinate'] =\
            simplify_coordinate(data['Lon'], data['Lat'])
    crimes_by_coordinate = data.groupby(by='coordinate').size()
    return crimes_by_coordinate


def simplify_coordinate(lon, lat):
    """ Combines coordinates into a tuple, after rounding them down """
    longitude = lon.round(2)
    latitude = lat.round(2)
    coordinates = [(x[0], x[1]) for x in zip(longitude, latitude)]
    return longitude, latitude, coordinates


def main():
    """ Main Function """
    # Import CSV if a Db file is not present, otherwise, open the db
    if not os.path.isfile('crime.pkl'): # and not os.path.isfile('crime.db'):
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

    # Simplify Coordinates & Sums up all crimes
    crimes_all = sum_of_crimes(data)

    # Creates Bokeh Data CDS
    data_dict = {'lon': [x[0] for x in crimes_all.index],
                 'lat': [x[1] for x in crimes_all.index],
                 'qty': [int(x) for x in crimes_all.values],
                 'size': [float(x) * 0.0003 for x in crimes_all.values]}
    data_cds = ColumnDataSource(data=data_dict)

    # Geographic Plots
    print('Creating General Crimes Bokeh Plot')
    map_opts = {'lat': 39.992003865395425,
                'lng': -75.14991150054124,
                'map_type': "roadmap",
                'zoom': 11}
    geoplot.plot_cds_geo(data_cds, map_opts, 'size', "crime_plot.html",
                         title="Philly Crimes")

    # Saves Pickle File
    # data.to_pickle('crime.pkl')

    # Saves SQL Database
    print('Creating Database')
    data.to_sql('Crime', conn, if_exists='replace', chunksize=1000)
    conn.close()

    return data, crimes_all


if __name__ == "__main__":
    data, crimes_all = main()
