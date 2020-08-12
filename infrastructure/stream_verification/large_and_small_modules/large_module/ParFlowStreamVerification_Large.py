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


# Print to standard error
def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

# Test if object is iterable.
# Argument: object to be tested.
# Returns : bool
#   - True if obj is an iterable object.
#   - False otherwise
def isiterable(obj):
  try:
    iter(obj)
  except Exception:
    return False
  else:
    return True

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

# Convert a station id from one of several possible formats into a common one
# Argument: int, float, or string representing a USGS station id number
# Returns: str
#   - String properly formatted (8 digit number) to be a station id
def station_id_cast( station_id ):
  if isinstance( station_id, int ):
    if station_id >= 0:
      return f"{station_id:0>8}"
    else:
      raise ValueError( f"station_id_cast given station id as negative integer {station_id}. Must be positive integer." )
  if isinstance( station_id, str ):
    return station_id_cast( int(station_id, 10) )
  if isinstance( station_id, float ):
    # check is int-able
    if int(math.ceil(station_id)) != int(math.floor(station_id)):
      raise ValueError( f"Cannot create station id from non-integer float {station_id}" )
    return station_id_cast( int(station_id) )

  raise ValueError( f"station_id_cast given station id as {type(station_id)}, can only handle int, str, and float" )

# Convert a parameter id from one of several possible formats into a common one
# Argument: int, float, or string representing a USGS parameter id number
# Returns: str
#  - String properly formatted (5 digit number) to be a parameter id
def parameter_id_cast( parameter_id ):
  if isinstance( parameter_id, int ):
    if parameter_id >= 0:
      return f"{parameter_id:0>5}"
    else:
      raise ValueError( f"parameter_id_cast given parameter id as negative integer {parameter_id}. Must be positive integer." )
  if isinstance( parameter_id, str ):
    return parameter_id_cast( int(parameter_id, 10) )
  if isinstance( parameter_id, float ):
    # check is int-able
    if int(math.ceil(parameter_id)) != int(math.floor(parameter_id)):
      raise ValueError( f"Cannot create parameter id from non-integer float {parameter_id}" )
    return parameter_id_cast( int(parameter_id) )

  raise ValueError( f"parameter_id_cast given parameter id as {type(parameter_id)}, can only handle ints, strings, and floats" )


# Known flow parameters used in this module
# Map from a parameter id to a name
parameter_id_name_map = {
  parameter_id_cast("00060") : "flow"
}
# Map from a name parameter id to a parameter id (uses existing parameter_id_name_map).
# NOTE: Assumes all parameters have different names.
parameter_name_id_map = { value : key for key, value in parameter_id_name_map.items() }

# map from parameter id to its units
parameter_id_units_map = {
  parameter_id_cast("00060") : "cms"
}

# Default parameter id used in this module
# Currently the "flow" parameter
default_parameter_id = parameter_name_id_map["flow"]


# Load station's parameter data from USGS
# Arguments:
#   - station_id : object representing a station id.
#   - parameter_id : object representing a parameter id (default: default_parameter_id)
#   - start_date : start of time period  (default: None)
#   - end_date : end of time period  (default: None)
#   - date_range : list of dates (default: None)
# Note about usage: Must either use start_date and end_date, or date_range.
#                   If both are used, date_range is the source of the dates
# Returns: pandas.DataFrame
#   - Columns: "date", "{parameter_id}"
#   - Rows: observations from station
def load_station_data_over_date_range_as_DataFrame( station_id, parameter_id=default_parameter_id, start_date=None, end_date=None, date_range=None ):
  # Check proper usage of date parameters
  if (start_date is None or end_date is None) and date_range is None:
    raise ValueError("load_station_data_over_date_range_as_DataFrame must use either both start and end dates, or date_range")

  # Properly cast station and parameter ids
  station_id = station_id_cast( station_id )
  parameter_id = parameter_id_cast( parameter_id )

  # Create date-range
  # From provided time-period parameters
  if date_range is None:
    date_range_list = pd.date_range( start=start_date, end=end_date ).tolist()
  # From provided list of dates
  elif isinstance( date_range, list ):
    date_range_list = sorted( date_range )
  # From provided pandas DatetimeIndex
  elif isinstance( date_range, pandas.core.indexes.datetimes.DatetimeIndex ):
    date_range_list = date_range.tolist()

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
      "date"       : date_value_object.date,
      parameter_id : date_value_object.value
    }
    for request in station_requests
    for date_value_object in request.data
  )

  # Create DatFrame from the flattened generator.
  station_data = pd.DataFrame(
    columns = ["date", parameter_id],
    data    = list(flattened_data_generator),
  ).sort_values("date")

  if station_data.index.size == 0:
    raise RuntimeError(f"Station {station_id} does not have data for parameter {parameter_id} for date range {using_start_date} - {using_end_date}")

  return station_data

# Load the station-id-to-parflow-x-y mapping CSV file as a pandas.DataFrame object
# Argument:
#    path_to_stations_table (str) : path to stations-parflow mapping CSV file
# Returns: pandas.DataFrame
#   - Rows and columns are same as the CSV document.
def load_station_mapping_as_DataFrame( path_to_stations_table ):
  return pd.read_csv( path_to_stations_table )

# Class for containing statistical analysis of a parflow vs station observations comparison
@dataclass
class EvaluationReport:
  # Parameter ID of values being compared
  parameter_id: str
  # Number of observation in each group
  N: int
  percent_bias: float
  spearman_rho: float
  spearman_rho_p: float
  r_squared: float
  root_mean_squared_error: float

  # Create string representation of report.
  # Returns: str
  def __str__(this):
    return f"N: {this.N}\n% Bias: {this.percent_bias}\nSpearman rho: {this.spearman_rho} (p={this.spearman_rho_p})\nR2: {this.r_squared}\nRMSE: {this.root_mean_squared_error}\n"

# Class for containing plots of values over time of specific parameter.
# Plots are figure.BaseTraceType objects (specifically plotly.graph_objects.Scatter objects)
# These are rendered in a plotly.graph_objects.Figure object
@dataclass
class EvaluationPlots:
  # Parameter ID of values being plotted
  parameter_id: str
  # Plot of values observed by station
  observed: plotly.basedatatypes.BaseTraceType
  # Plot of values simulated by ParFlow
  simulated: plotly.basedatatypes.BaseTraceType
  # Difference between the two values (simulated - observed)
  # Note: Optional
  difference: plotly.basedatatypes.BaseTraceType = None

  # get all non-None plots as a list object
  # Returns: list
  #   - Contains all plots which are not None.
  def get_plots_as_list(this):
    if plotly.basedatatypes.BaseTraceType != None:
      return [this.observed, this.simulated, this.difference]
    else:
      return [this.observed, this.simulated]


# Class for containing EvaluationReport and EvaluationPlots from a station/parflow comparision
# See below for member variables and their description
@dataclass
class EvaluationReportAndPlot:
  # Station ID for observed values
  station_id: str
  # Parameter ID of values being plotted
  parameter_id: str
  # Report object
  report: EvaluationReport
  # Plot object
  plots: EvaluationPlots

# Class for containing EvaluationReport and EvaluationPlots from a station/parflow comparision
# Grouped by daily, weekly, and monthly averages.
# See below for member variables and their description
class DailyWeeklyMonthlyEvaluation:
  def __init__(this, daily, weekly, monthly ):
    # Station ID for observed values
    this.station_id = daily.station_id
    # Parameter ID of values being plotted
    this.parameter_id = daily.parameter_id

    # Note: Currently assuming that all groupings are on the same IDs
    # EvaluationReportAndPlot of a daily comparison
    this.daily = daily
    # EvaluationReportAndPlot of a average weekly comparison
    this.weekly = weekly
    # EvaluationReportAndPlot of a average monthly comparison
    this.monthly = monthly

  # Display all plots
  def display_plots( this ):
    parameter_name = parameter_id_name_map[this.parameter_id]
    parameter_units = parameter_id_units_map[this.parameter_id]
    title = f"Comparison of {parameter_name} between Station {this.station_id} and ParFlow"
    xaxis = dict( title="Date" )

    daily_figure = go.Figure(
      data = this.daily.plots.get_plots_as_list(),
      layout = dict(
        title = title,
        xaxis = xaxis,
        yaxis = dict( title=f"Daily {parameter_name} ({parameter_units})" )
      )
    )

    weekly_figure = go.Figure(
      data = this.weekly.plots.get_plots_as_list(),
      layout = dict(
        title = title,
        xaxis = xaxis,
        yaxis = dict( title = f"Average Weekly {parameter_name} ({parameter_units})" )
      )
    )

    monthly_figure = go.Figure(
      data = this.monthly.plots.get_plots_as_list(),
      layout = dict(
        title = title,
        xaxis = xaxis,
        yaxis = dict( title = f"Average Monthly {parameter_name} ({parameter_units})" )
      )
    )

    ipynb_display.display( daily_figure )
    ipynb_display.display( weekly_figure )
    ipynb_display.display( monthly_figure )

    # This was an implementation of plotting with sublots that was really just unnecessary
    # figure = plotly.subplots.make_subplots( rows=3, cols=1 )
    # # Daily plots
    # for trace in this.daily.plots.get_plots_as_list():
    #   # All the legends are the same, but we only want the one set of them
    #   # Show these legends
    #   trace.showlegend = True
    #   figure.add_trace( trace, row=1, col=1 )
    # figure.update_yaxes( title_text = f"Daily {parameter_name}", row=1, col=1 )
    #
    # # Weekly plots
    # for trace in this.weekly.plots.get_plots_as_list():
    #   # All the legends are the same, but we only want the one set of them
    #   # Do not show these legends
    #   trace.showlegend = False
    #   figure.add_trace( trace, row=2, col=1 )
    # figure.update_yaxes( title_text = f"Average Weekly {parameter_name}", row=2, col=1 )
    #
    # # Monthly plots
    # for trace in this.monthly.plots.get_plots_as_list():
    #   # All the legends are the same, but we only want the one set of them
    #   # Do not show these legends
    #   trace.showlegend = False
    #   figure.add_trace( trace, row=3, col=1 )
    # figure.update_yaxes( title_text = f"Average Monthly {parameter_name}", row=3, col=1 )
    #
    # # Set full subfigure title
    # figure.update_layout( title_text = f"Comparison of {parameter_name} between Station {this.station_id} and ParFlow" )
    # # Set X-axis title only on lowest figure
    # figure.update_xaxes(
    #   title_text = "Date",
    #   row=3, col=1
    # )
    #
    # # Display the figure
    # ipynb_display.display( figure )

  # Display all correlation information.
  def display_evaluation( this ):
    print( "Correlation:" )
    print( "\tSpearman Rho (p-value)" )
    print( f"\t\tDaily:   {this.daily.report.spearman_rho:.10f} (p={this.daily.report.spearman_rho_p:.10f})" )
    print( f"\t\tWeekly:  {this.weekly.report.spearman_rho:.10f} (p={this.weekly.report.spearman_rho_p:.10f})" )
    print( f"\t\tMonthly: {this.monthly.report.spearman_rho:.10f} (p={this.monthly.report.spearman_rho_p:.10f})" )

    print( "\tR-Squared" )
    print( f"\t\tDaily:   {this.daily.report.r_squared}" )
    print( f"\t\tWeekly:  {this.weekly.report.r_squared}" )
    print( f"\t\tMonthly: {this.monthly.report.r_squared}" )

    print( "\tRMSE" )
    print( f"\t\tDaily:   {this.daily.report.root_mean_squared_error}" )
    print( f"\t\tWeekly:  {this.weekly.report.root_mean_squared_error}" )
    print( f"\t\tMonthly: {this.monthly.report.root_mean_squared_error}" )

  # Display plots and correlation information
  def display( this ):
    this.display_plots()
    this.display_evaluation()


# In the below code, there are several points where new columns are created and used.
# These suffixes are what are used in several code sections to differentiate columns with the same name from different sources
# Note: It is rare that they are used directly, instead use get_observed_simulated_column_names_from_parameter_id if possible.
observed_suffix = "_observed"
simulated_suffix = "_simulated"


# Get the names for columns as tuple in order 'observed name', 'simulated name'
# Returns: tuple( str )
#   - return_value[0] : column name for observed value
#   - return_value[1] : column name for simulated value
def get_observed_simulated_column_names_from_parameter_id( parameter_id=default_parameter_id ):
  return f"{parameter_id}{observed_suffix}", f"{parameter_id}{simulated_suffix}"


# Perform statistical analysis of observed vs simulated values of the specified parameter.
# Arguments:
#   - data: pandas.DataFrame containing all dates, observed values, and simulated values to be compared.
#           Must have columns "date", and observed and simulated columns for the parameter as given by get_observed_simulated_column_names_from_parameter_id
#   - parameter_id (optional) : ID of parameter to perform evaluation on. (default: default_parameter_id)
# Returns:
#   - EvaluationReport
# Side Effects
#   - data will be updated with the following columns:
#     + "difference_{parameter_id}": data[simulated_column] - data[observed_column]
#     + "difference_squared_{parameter_id}": : (data[simulated_column] - data[observed_column])^2
def evaluate_station_vs_parflow( data, parameter_id=default_parameter_id ):
  # Get names for the observed and simulated columns for the parameter id
  observed_column, simulated_column = get_observed_simulated_column_names_from_parameter_id( parameter_id )
  difference_column = f"difference_{parameter_id}"
  difference_squared_column = f"difference_squared_{parameter_id}"

  # Compute differences if not already available
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

  return EvaluationReport(
    parameter_id            = parameter_id,
    N                       = N,
    percent_bias            = percent_bias,
    spearman_rho            = spearman_rho,
    spearman_rho_p          = spearman_rho_p,
    r_squared               = r_squared,
    root_mean_squared_error = root_mean_squared_error
  )


# Create plots of observed vs simulated values of the specified parameter.
# Arguments:
#   - data: pandas.DataFrame containing all dates, observed values, and simulated values to be compared.
#           Must have columns "date", and observed and simulated columns for the parameter as given by get_observed_simulated_column_names_from_parameter_id
#           For the difference plot to be created, must also have the column "difference_{parameter_id}" which is usually created by evaluate_station_vs_parflow
#   - parameter_id (optional) : ID of parameter to perform evaluation on. (default: default_parameter_id)
# Returns: EvaluationPlots
#          Note: if "difference_{parameter_id}" is not a column in "data", then EvaluationPlots.difference will be None
def plot_station_vs_parflow( data, parameter_id=default_parameter_id ):
  observed_column, simulated_column = get_observed_simulated_column_names_from_parameter_id( parameter_id )
  difference_column = f"difference_{parameter_id}"

  station_plot = go.Scatter(
    x    = data["date"],
    y    = data[observed_column],
    name = "Actual",
    mode = "lines+markers",
    line = dict(
      color = "green"
    )
  )
  parflow_plot = go.Scatter(
    x    = data["date"],
    y    = data[simulated_column],
    name = "ParFlow",
    mode = "lines+markers",
    line = dict(
      color = "orange"
    )
  )

  if difference_column in data.columns:
    difference_plot = go.Scatter(
      x    = data["date"],
      y    = data[difference_column],
      name = "True Difference (ParFlow - Station)",
      mode = "lines+markers",
      line = dict(
        color = "red"
      )
    )
  else:
   difference_plot = None

  return EvaluationPlots(
    parameter_id = parameter_id,
    observed     = station_plot,
    simulated    = parflow_plot,
    difference   = difference_plot
  )


# Perform statistical analysis and plotting of observed vs simulated data and recieve results as an EvaluationReportAndPlot object
# Arguments:
#   - data: pandas.DataFrame containing all dates, observed values, and simulated values to be compared.
#           Must have columns "date", and observed and simulated columns for the parameter as given by get_observed_simulated_column_names_from_parameter_id
#   - station_id: ID of station that the observed data is from
#   - parameter_id (optional) : ID of parameter to perform evaluation on. (default: default_parameter_id)
# Returns: EvaluationReportAndPlot
# Side Effects
#   - data will be updated (by evaluate_station_vs_parflow) with the following columns:
#     + "difference_{parameter_id}": data[simulated_column] - data[observed_column]
#     + "difference_squared_{parameter_id}": (data[simulated_column] - data[observed_column])^2
def perform_evaluation( data, station_id, parameter_id=default_parameter_id ):
  # ipynb_display.display( data )
  # Note computes differences, updating 'data' which allows 'plot_station_vs_parflow' to plot differences
  report = evaluate_station_vs_parflow( data, parameter_id )
  plots = plot_station_vs_parflow( data, parameter_id )

  return EvaluationReportAndPlot( station_id, parameter_id, report, plots )


# Perform multiple, grouped statistical analysis and plotting of observed vs simulated data and recieve results as an DailyWeeklyMonthlyEvaluation object
# Performs evaluation in 3 groups:
#   - Daily: Analysis with all daily data represented.
#   - Weekly: Analysis with data averaged by week.
#   - Monthly: Analysis with data averaged by month.
# Arguments:
#   - data: pandas.DataFrame containing all dates, observed values, and simulated values to be compared.
#           Must have columns "date", "week", and "month", and observed paramter and simulated parameter as given by get_observed_simulated_column_names_from_parameter_id
#   - station_id: ID of station that the observed data is from
#   - parameter_id (optional) : ID of parameter to perform evaluation on. (default: default_parameter_id)
# Returns: DailyWeeklyMonthlyEvaluation
# Side Effects
#   - data will be updated (by evaluate_station_vs_parflow) with the following columns:
#     + "difference_{parameter_id}": data[simulated_column] - data[observed_column]
#     + "difference_squared_{parameter_id}": (data[simulated_column] - data[observed_column])^2
def perform_grouped_evaluation( data, station_id, parameter_id=default_parameter_id ):
  station_id = station_id_cast( station_id )

  observed_column, simulated_column = get_observed_simulated_column_names_from_parameter_id( parameter_id )

  # Do evaluation of daily data
  daily_evaluation = perform_evaluation( data, station_id, parameter_id )

  # Do evaluation of weekly data (averaged)
  weekly_grouped_data = data.groupby( "week", as_index=False ).aggregate( {"date" : "first", observed_column : "mean", simulated_column : "mean"} )
  weekly_evaluation = perform_evaluation( weekly_grouped_data, station_id, parameter_id )

  # Do evaluation of monthly data (averaged)
  monthly_grouped_data = data.groupby( "month", as_index=False ).aggregate( {"date" : "first", observed_column : "mean", simulated_column : "mean"} )
  monthly_evaluation = perform_evaluation( monthly_grouped_data, station_id, parameter_id )

  return DailyWeeklyMonthlyEvaluation(daily_evaluation, weekly_evaluation, monthly_evaluation )


# Collect station observations for parameter and compare agains provided parflow simulation results.
# Arguments:
#   - start_date: Date to begin collecting observations from.
#   - end_date: Date to end collecting observations from.
#   - parflow_data: pandas.DataFrame object with columns: "date", "station_id" and "{parameter_id}"
#   - station_id: ID of station to collect observation data from.
#   - parameter_id (optional) : ID of parameter to perform evaluation on. (default: default_parameter_id)
# Returns: tuple( DailyWeeklyMonthlyEvaluation, pandas.DataFrame )
#   - returned DataFrame is the station data and parflow data joined on the date.
#     DataFrame has following columns:
#       + "date": date of observation
#       + "week": number of 7 day periods between first date and this row's date
#       + "month": number of 31 day periods between first date and this row's date
#       + observed parameter and simulated parameter given by by get_observed_simulated_column_names_from_parameter_id
#       + difference_{parameter_id}": data[simulated parameter] - data[observed parameter]
#       + difference_squared_{parameter_id}": (data[simulated parameter] - data[observed parameter])^2
# Assumptions:
#   1. ParFlow has rows with "station_id" values that match the "station_id" function argument.
def compare_parflow_vs_station_across_daterange( start_date, end_date, parflow_data, station_id, parameter_id=default_parameter_id ):

  # Filter ParFlow data down to this station.
  parflow_station_data = parflow_data[ parflow_data["station_id"] == station_id ].sort_values("date")

  # Load Station Data
  station_data = load_station_data_over_date_range_as_DataFrame( station_id=station_id, parameter_id=parameter_id, start_date=start_date, end_date=end_date )

  # Check if the collection of dates are unequal.
  # Note: the use of DataFrame.unique() instead of just set() is a performance optimization.
  parflow_date_set = set( parflow_station_data["date"].unique() )
  station_date_set = set( station_data["date"].unique() )
  if parflow_date_set != station_date_set:
    eprint( "The input ParFlow data and the recieved station data have different sets of dates. Checking if evaluation can continue." )
    # Check if there is at least some overlap
    date_intersection = parflow_date_set.intersection( station_date_set )
    date_union = parflow_date_set.union( station_date_set )
    if len(date_intersection) == 0:
      raise RuntimeError( "The input ParFlow data and the recieved station data do not have any dates in common." )
    else:
      eprint( f"The input ParFlow data and the recieved station data share {len(date_intersection)} of {len(date_union)} dates. Continuing evaluation." )

  # Do inner-join between station and parflow data, on date.
  # Will not include any dates that are not in *both* collections
  # Overlapping keys (namely the column containing the parameter values) are
  # given the proper observed/simulatedsuffix
  data = station_data.join(
    parflow_station_data[["date", parameter_id]].set_index("date"),
    on = "date",
    how = "inner",
    lsuffix = observed_suffix,
    rsuffix = simulated_suffix
  )

  # Add week and month columns to 'data' for temporal grouping.
  # Indicates how many *full* weeks and months since first date
  # (As opposed the calendar week month)
  data["day"] = (data[["date"]] - data["date"].min()).apply(
    axis        = "columns",
    result_type = "expand",
    func        = lambda x : int( pd.Timedelta(x.values[0]).days )
  )
  data["week"] = data["day"] // 7    # Integer division to get week groups
  data["month"] = data["day"] // 31  # Integer division to get month groups

  full_evaluations = perform_grouped_evaluation( data, station_id, parameter_id )

  return full_evaluations, data
