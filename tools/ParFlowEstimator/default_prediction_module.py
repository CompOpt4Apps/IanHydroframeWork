import math

def module_default_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return predict_footprint_from_size( NX, NY, NZ, timesteps )

def module_default_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps )

def predict_footprint_from_size( NX, NY, NZ, timesteps):
  nx, ny, nz = NX, NY, NZ
  prediction =  0.00816995598709359*nx**2 \
              + 6.69251873916153*nx*ny    \
              - 25.2516520661043*nx       \
              + 0.00041536449776633*ny**2 \
              + 61.8637631577788*ny       \
              + 30486.0155720958
  return dict(
    value=max( 0.0, prediction ),
    error_bound=170786.46950405478,
    unit="kilobyte"
  )

def predict_runtime_from_size_and_timesteps( NX, NY, NZ, timesteps ):
  nx, ny, nz = NX, NY, NZ
  prediction =   6.89426918589472e-6*nx**2 \
               + 8.89970972641197e-5*nx*ny \
               - 0.0416086434219884*nx     \
               + 8.56467620796192e-6*ny**2 \
               - 0.0448171870718721*ny     \
               + 23.545234649138
  return dict(
    #TODO: Replace with accurate model.
    #NOTE: Below model is for code testing purposes only.
    value=max( 0.0, prediction ),
    error_bound=47.95722951718799,
    unit="second"
  )
