import math

def footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return predict_footprint_from_size( NX, NY, NZ )

def runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps )


def alt_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return math.log2( predict_footprint_from_size( NX, NY, NZ ) )

def alt_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return math.sqrt( predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps ) )


def predict_footprint_from_size( NX, NY, NZ ):
  return NX*806.6720 + NY*815.8475 + NX*NY*4.8494  +  (NX**2)*0.0178 + (NY**2)*0.0154

def predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps ):
  return .000001*NX*NY*NZ*timesteps
