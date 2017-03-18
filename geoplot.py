#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper Functions to create a Bokeh Google Maps Plot
"""

from bokeh.io import output_file, save
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource, Circle,
                          DataRange1d, HoverTool, PanTool, ZoomInTool,
                          ZoomOutTool, WheelZoomTool, BoxSelectTool, ResetTool)


def df_to_cds(data_df, columns):
    """ Converts a DataFrame to a ColumnDataSource for the list of columns
        we want to take with us to a ColumnDataSource
    """
    data_dict = {}
    for column in columns:
        data_dict[column] = [float(x) for x in data_df[column].tolist()]
    return ColumnDataSource(data=data_dict)


def plot_cds_geo(data_cds, map_opts_dict, size_col, out_path,
                 x_col='lon', y_col='lat', leg_col='Data', title='Bokeh Plot',
                 gmap_api='gmap_api.txt'):
    """ Plots a ColumnDataSource against Google Maps

        Mandatory Inputs:
        data_cds: ColumnDataSource object to plot, must contain the below cols.
                  It should have a 'lon' and 'lat' column.
        map_opts_dict: GMapOptions object to use for map_options
        size_col: Either a column in data_cds to use or some number for each
                  point's size
        out_path: Path and/or file name where to save the plot to

        Optional Inputs:
        x_col: Column in data_cds to use for the longitude [Default = 'lon']
        y_col: Column in data_cds to use for the latitude [Default = 'lat']
        title: String for the Bokeh title [Default = 'Bokeh Plot']
        gmap_api: Path to a text file with the Google Maps API Key
                  [Default = './gmap_api.txt']
    """
    # Initializes Plot
    map_opts = GMapOptions(lat=map_opts_dict['lat'],
                           lng=map_opts_dict['lng'],
                           map_type=map_opts_dict['map_type'],
                           zoom=map_opts_dict['zoom'])
    plot = GMapPlot(x_range=DataRange1d(), y_range=DataRange1d(),
                    width=750, height=500, map_options=map_opts)
    plot.title.text = title

    # Loads Gmap API Key
    try:
        with open(gmap_api, 'r') as gmap_file:
            plot.api_key = gmap_file.readline().strip()
    except Exception as err:
        print('No Google API Key foound in {}'.format(gmap_api))
        print(err)

    # Creates Points on Plot
    circle = Circle(x=x_col, y=y_col, size=size_col,
                    fill_color="blue", fill_alpha=0.8, line_color=None)
    plot.add_glyph(data_cds, circle)

    # Adds Interactive Tools and saves Plot
    hover = False  # Not ready for prime time
    if hover:
        val = '@{}'.format(size_col)
        tips = [("(x,y)", "($x, $y)"), ("desc", val)]
        plot.add_tools(PanTool(), WheelZoomTool(), ZoomInTool(), ZoomOutTool(),
                       BoxSelectTool(), HoverTool(tooltips=tips), ResetTool())
    else:
        plot.add_tools(PanTool(), WheelZoomTool(), ZoomInTool(), ZoomOutTool(),
                       BoxSelectTool(), ResetTool())
    output_file(out_path)
    save(plot)