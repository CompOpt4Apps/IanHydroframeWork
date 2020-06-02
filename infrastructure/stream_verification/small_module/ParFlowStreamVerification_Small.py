import os, sys, fileinput, random, datetime
import re, json, csv
import itertools, collections
import numpy, pandas, math, scipy, scipy.stats
import plotly
import climata

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import climata.usgs as usgs
import IPython.core.display as ipynb_display

from functools import reduce
# from collections import namedtuple
from dataclasses import dataclass
from math import sqrt

from numpy import nan
from pprint import pprint, pformat

flow_parameter_id = "00060"
flow_parameter_name = "flow"

parameter_id = flow_parameter_id
parameter_name = flow_parameter_name

observed_column = f"{parameter_name}_observed"
simulated_column = f"{parameter_name}_simulated"
difference_column = f"{parameter_name}_difference"
difference_squared_column = f"{parameter_name}_difference_squared"

# Convert list of same-keyed-dictinaries into dictionary of lists
# Arguments: One or more individual dictionaries or iterable of dictionaries, where all dictionaries have the same keys.
# Returns: dict
#   - The resulting dictionary has all keys of the Arguments
#   - The value of each key is a list of the values of all the dictionaries' value for that key in order they appear in the invocation
def merge_dictionary_lists( *arg_dictionaries ):
  if len(arg_dictionaries) == 0:
    return dict()

  dictionaries = []
  for arg in arg_dictionaries:
    # For dictionaries as arguments
    if isinstance(arg, dict):
      dictionaries.append( arg )
    # For iterables of dictionaries as arguments
    # Note: Assuming (mostly correctly) that there is no nesting of iterables within iterables.
    #      e.g. will never invoke this function as merge_dictionary_lists( [ [ {...}, ... ], ... ] )
    elif isiterable(arg):
      dictionaries.extend( arg )

  # Simply use keys from first dictionary
  keys = set( dictionaries[0].keys() )
  # Ensure that all dictionaries have these keys
  if len(dictionaries) > 1:
    for d in dictionaries[1:]:
      if set(d.keys()) != keys:
        raise ValueError( "All dictionaries in merge_dictionary_lists must have same keys" )

  result_dict = {
    key : list( itertools.chain( *( list(d[key]) for d in dictionaries ) ) )
    for key in keys
  }

  return result_dict

# Load the station-id-to-parflow-x-y mapping CSV file as a pandas.DataFrame object
# Argument:
#    path_to_stations_table (str) : path to stations-parflow mapping CSV file
# Returns: pandas.DataFrame
#   - Rows and columns are same as the CSV document.
def load_station_mapping_as_DataFrame( path_to_stations_table ):
  return pd.read_csv( path_to_stations_table )

# Load station's parameter data from USGS
# Arguments:
#   - station_id : object representing a station id.
#   - start_date : start of time period
#   - end_date : end of time period
# Returns: pandas.DataFrame
#   - Columns: "date",  parameter_name (see top of file about name)
#   - Rows: observations from station
def load_station_data_over_date_range_as_DataFrame( station_id, start_date, end_date ):
  # Create date-range
  date_range_list = pd.date_range( start=start_date, end=end_date ).tolist()

  using_start_date = date_range_list[0]
  using_end_date = date_range_list[-1]
  # Download station data
  station_requests = usgs.DailyValueIO(
    start_date = using_start_date,
    end_date   = using_end_date,
    station    = station_id,
    parameter  = parameter_id
  )
  # climata.usgs.DailyValueIO claims to be iterable, but in practice there is nothing to iterate over...
  # Note the IO obeject annot be exhausted
  #(ie, it can be iterated over multiple times to get the different aspects of the request(s) from it)

  # Flatten data into list of dictionaries with the data and flow extracted
  # Note this is a generator, which *CAN* be exhausted. Only use *ONCE*!
  flattened_data_generator = (
    {
      "date"          : date_value_object.date,
       parameter_name : date_value_object.value
    }
    for request in station_requests
    for date_value_object in request.data
  )

  # Create DatFrame from the flattened generator.
  station_data = pd.DataFrame(
    columns = ["date", parameter_name],
    data    = list(flattened_data_generator),
  ).sort_values("date")

  if station_data.index.size == 0:
    raise RuntimeError(f"Station {station_id} does not have data for \"{parameter_name}\" for date range {using_start_date} - {using_end_date}")

  return station_data


# Take data frame with dates and observed/simulated values, perform statistical analysis and create scatter plot objects (for later display)
# Argument:
#   - data (pandas.DataFrame): must have columns "date", observed_column, and simulated_column (see top of file about names)
# Returns: dictionary with following keys
#   - N
#   - percent_bias
#   - spearman_rho
#   - spearman_rho_p
#   - r_squared
#   - root_mean_squared_error
#   - station_plot: plotly.graph_objects.Scatter object plotting the stations actual observed data.
#   - parflow_plot: plotly.graph_objects.Scatter object plotting parflows actual simulated data.
#   - difference_plot: plotly.graph_objects.Scatter object plotting the difference (parflow - station) between them
# Side Effects
#   - data will be updated with the following columns (see top of file about names)
#     + difference_column: data[simulated_column] - data[observed_column]
#     + difference_squared_column: (data[simulated_column] - data[observed_column])^2
def perform_evaluation( data ):
  # Compute differences if not already available (assumes that all differences exist if column exists)
  # Note: This updates the data DataFrame and the change is visable to the caller
  #       No need to explicitly return the updated DataFrame
  if difference_column not in data.columns:
    data[difference_column] = data[simulated_column] - data[observed_column]
  if difference_squared_column not in data.columns:
    data[difference_squared_column] = data[difference_column].pow(2)

  # Compute commonly used sub-expressions
  N = data.index.size
  sum_difference = data[difference_column].sum()
  sum_difference_squared = data[difference_squared_column].sum()
  total_sum_squared_observed = (data[observed_column] - data[observed_column].mean()).pow(2).sum()

  # Compute desired statistics
  percent_bias = ( sum_difference / data[observed_column].sum() )*100
  # For scipy.stats.spearmanr, I am not under the impression that the order matters
  spearman_rho, spearman_rho_p = scipy.stats.spearmanr( data[simulated_column], data[observed_column] )
  r_squared = 1 - ( sum_difference_squared / total_sum_squared_observed )
  root_mean_squared_error = np.sqrt( sum_difference_squared / N )

  return dict(
    N                       = N,
    percent_bias            = percent_bias,
    spearman_rho            = spearman_rho,
    spearman_rho_p          = spearman_rho_p,
    r_squared               = r_squared,
    root_mean_squared_error = root_mean_squared_error,
    station_plot  = go.Scatter(
      x    = data['date'],
      y    = data[observed_column],
      name = "Actual",
      mode = "lines+markers",
      line = dict(
        color = "green"
      )
    ),
    parflow_plot = go.Scatter(
      x    = data['date'],
      y    = data[simulated_column],
      name = "ParFlow",
      mode = "lines+markers",
      line = dict(
        color = "orange"
      )
    ),
    difference_plot = go.Scatter(
      x    = data['date'],
      y    = data[difference_column],
      name = "True Difference (ParFlow - Station)",
      mode = "lines+markers",
      line = dict(
        color = "red"
      )
    )
  )


# Performs full USGS data download, comparison, and plotting of station vs parflow simulated data.
# Arguments:
#   - parflow_data: pandas.DataFrame object with columns: "date", "station_id" and "{parameter_id}"
#   - station_id: ID of station to collect observation data from.
#   - start_date: Date to begin collecting observations from.
#   - end_date: Date to end collecting observations from.
# Returns: pandas.DataFrame of all data used in evaluation
#   - returned DataFrame is the station data and parflow data joined on the date.
#     DataFrame has following columns:
#       + "date": date of observation
#       + "week": number of 7 day periods between first date and this row's date
#       + "month": number of 31 day periods between first date and this row's date
#       + observed parameter: values for parameter as observed from station
#       + simulated parameter: values for parameter as simulated by parflow
#       + difference_column: data[simulated parameter] - data[observed parameter]
#       + difference_squared_column: (data[simulated parameter] - data[observed parameter])^2
# Assumptions:
#   1. ParFlow has rows with "station_id" values that match the "station_id" function argument.
def compare_and_display( parflow_data, station_id, start_date, end_date ):
  # Filter ParFlow data down to this station.
  parflow_station_data = parflow_data[ parflow_data['station_id'] == station_id ].sort_values("date")

  # Load Station Data
  station_data = load_station_data_over_date_range_as_DataFrame( station_id, start_date, end_date )
  # Create date-range
  date_range_list = pd.date_range( start=start_date, end=end_date ).tolist()

  using_start_date = date_range_list[0]
  using_end_date = date_range_list[-1]
  # Download station data
  station_requests = usgs.DailyValueIO(
    start_date = using_start_date,
    end_date   = using_end_date,
    station    = station_id,
    parameter  = parameter_id
  )
  # climata.usgs.DailyValueIO claims to be iterable, but in practice there is nothing to iterate over...
  # Note the IO obeject annot be exhausted
  #(ie, it can be iterated over multiple times to get the different aspects of the request(s) from it)

  # Flatten data into list of dictionaries with the data and flow extracted
  # Note this is a generator, which *CAN* be exhausted. Only use *ONCE*!
  flattened_data_generator = (
    {
      "date"         : date_value_object.date,
      parameter_name : date_value_object.value
    }
    for request in station_requests
    for date_value_object in request.data
  )

  # Create DatFrame from the flattened generator.
  station_data = pd.DataFrame(
    columns = ['date', parameter_name],
    data = list(flattened_data_generator),
  ).sort_values("date")

  # Join
  data = station_data.join(
    parflow_station_data[['date', parameter_name]].set_index("date"),
    on = "date",
    how = "inner",
    lsuffix = "_observed",
    rsuffix = "_simulated"
  )

  # Add week and month columns to 'data' for temporal grouping.
  # Indicates how many *full* weeks and months since first date
  # (As opposed the calendar week month)
  data['day'] = (data[['date']] - data['date'].min()).apply(
    axis        = "columns",
    result_type = "expand",
    func        = lambda x : int( pd.Timedelta(x.values[0]).days )
  )
  data['week'] = data['day'] // 7    # Integer division to get week groups
  data['month'] = data['day'] // 31  # Integer division to get month groups

  daily_evaluation   = perform_evaluation( data )
  weekly_evaluation  = perform_evaluation( data.groupby( "week",  as_index=False ).aggregate( {"date" : "first", observed_column : "mean", simulated_column : "mean"} ) )
  monthly_evaluation = perform_evaluation( data.groupby( "month", as_index=False ).aggregate( {"date" : "first", observed_column : "mean", simulated_column : "mean"} ) )

  title = f"Comparison of Flow between Station {station_id} and ParFlow"
  xaxis = dict( title="Date" )

  daily_figure = go.Figure(
    data = [ daily_evaluation['station_plot'], daily_evaluation['parflow_plot'], daily_evaluation['difference_plot'] ],
    layout = dict(
      title = title,
      xaxis = xaxis,
      yaxis = dict( title=f"Daily Flow (cms)" )
    )
  )

  weekly_figure = go.Figure(
    data = [ weekly_evaluation['station_plot'], weekly_evaluation['parflow_plot'], weekly_evaluation['difference_plot'] ],
    layout = dict(
      title = title,
      xaxis = xaxis,
      yaxis = dict( title = f"Average Weekly Flow (cms)" )
    )
  )

  monthly_figure = go.Figure(
    data = [ monthly_evaluation['station_plot'], monthly_evaluation['parflow_plot'], monthly_evaluation['difference_plot'] ],
    layout = dict(
      title = title,
      xaxis = xaxis,
      yaxis = dict( title = f"Average Monthly Flow (cms)" )
    )
  )

  ipynb_display.display( daily_figure )
  ipynb_display.display( weekly_figure )
  ipynb_display.display( monthly_figure )

  print( "Correlation:" )
  print( "\tSpearman Rho (p-value)" )
  print( f"\t\tDaily:   {daily_evaluation['spearman_rho']:.10f} (p={daily_evaluation['spearman_rho_p']:.10f})" )
  print( f"\t\tWeekly:  {weekly_evaluation['spearman_rho']:.10f} (p={weekly_evaluation['spearman_rho_p']:.10f})" )
  print( f"\t\tMonthly: {monthly_evaluation['spearman_rho']:.10f} (p={monthly_evaluation['spearman_rho_p']:.10f})" )

  print( "\tR-Squared" )
  print( f"\t\tDaily:   {daily_evaluation['r_squared']}" )
  print( f"\t\tWeekly:  {weekly_evaluation['r_squared']}" )
  print( f"\t\tMonthly: {monthly_evaluation['r_squared']}" )

  print( "\tRMSE" )
  print( f"\t\tDaily:   {daily_evaluation['root_mean_squared_error']}" )
  print( f"\t\tWeekly:  {weekly_evaluation['root_mean_squared_error']}" )
  print( f"\t\tMonthly: {monthly_evaluation['root_mean_squared_error']}" )

  return data
