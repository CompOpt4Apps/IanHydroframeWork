#NOTE! This is merely a code example demonstrating prediction module implementation!
#NOTE! The "models" are for code demonstration purposes only, and have no relation to reality!
#NOTE! DO NOT USE THIS MODULE OR THE CODE IN IT FOR ANY MODELING OR ESTIMATION PURPOSES WHAT-SO-EVER!
import math

def module_default_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return dict(
    value=( ((NX*NY*NZ)/(number_processes_X*number_processes_Y*number_processes_Z))*number_processes_X*number_processes_Y*number_processes_Z*1.2+((NX*NY*NZ)*timesteps*.00000001) ),
    error_bound=0.5772156649
    unit="kilobyte"
  )

def module_default_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return dict(
    value=( ((NX*NY*NZ)/(number_processes_X*number_processes_Y*number_processes_Z))*timesteps*1.16925 ),
    error_bound=1.618033,
    unit="second"
  )

def timmys_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return i_hope_this_is_right_who_knows( NX, NY, NZ, timesteps)

# Do not use --runtime-prediction-function on this function! Use --runtime-prediction-function timmys_runtime_prediction_function
def i_hope_this_is_right_who_knows( x, y, z, T ):
  return dict(
    value=( pow( 1.0001, x*y*z*T ) ),
    error_bound=3.1415962,
    unit="second"
  )
