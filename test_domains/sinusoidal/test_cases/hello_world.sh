#!/usr/bin/env bash
test_name=hello_world

#set number of cells
number_cells_X=100
number_cells_Y=200
number_cells_Z=10

# Run for 24 hours
number_timesteps=24

# 8 processes, making 4 partitions in the X dimension, and 2 in the Y.
number_processes_X=4
number_processes_Y=2
number_processes_Z=1

# Create path to actual run script
# Change if moving script somewhere other than test_domains/sinusoidal/test_cases
path_to_scripts=${path_to_scripts:-$(readlink -f $0 | sed "s|test_cases/$(basename $0)|scripts|g")}

# Invoke run script
#   Process topology, X Y Z
#   Grid layout, X Y Z
#   Timesteps
#   Test Name
${path_to_scripts}/run.sh \
  ${number_processes_X} ${number_processes_Y} ${number_processes_Z} \
  ${number_cells_X}     ${number_cells_Y}     ${number_cells_Z} \
  ${number_timesteps} \
  ${test_name}
