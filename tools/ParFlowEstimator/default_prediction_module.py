import math

def module_default_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return predict_footprint_from_size( NX, NY, NZ )

def module_default_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps )


def alt_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return dict(
    value=predict_footprint_from_size( NX, NY, NZ ),
    unit="kilobyte"
  )

def alt_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return dict(
    value=predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps ),
    unit="second"
  )

def predict_footprint_from_size( NX, NY, NZ ):
  return dict(
    #TODO: Replace with more accurate model
    #NOTE: Currently this model returns invalid (negative) values for small domains.
    value=max( 0, -303000.3309 + NX*806.6720 + NY*815.8475 + NX*NY*4.8494  +  (NX**2)*-0.0178 + (NY**2)*-0.0154 ),
    unit="kilobyte"
  )

def predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps ):
  return dict(
    #TODO: Replace with accurate model.
    #NOTE: Below model is for code testing purposes only.
    value=.000001*NX*NY*NZ*timesteps,
    unit="second"
  )
