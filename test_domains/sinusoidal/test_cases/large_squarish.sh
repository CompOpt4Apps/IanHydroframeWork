#!/usr/bin/env bash
# Job will use 1 node, 28 cores, and 168gb of memory total.
#PBS -l select=1:ncpus=28:mem=168gb:pcmem=6gb
#PBS -q standard
#PBS -N large_squarish_ocelote_big_sinusoidal
#PBS -W group_list=mstrout
#PBS -l place=pack:exclhost
#PBS -l walltime=1:00:00
#PBS -j oe

# These parameters were pre-set to fill an Ocelote node's 168GB of usable RAM.
# You are free to adjust them as you'd like, but know that this test already
# consumes a significant amount of memory and time, and that the PBS system
# has little mercy for oversubscription of either.
NP=1
NQ=1
NR=1
NX=4935
NY=5000
NZ=5
NT=2
size_string=${NX}x${NY}x${NZ}-${NT}_${NP}-${NQ}-${NR}
test_name=ocelote_large_squarish_${size_string}

#▉    ▉  ▉▉▉▉▉▉   ▉   ▉           ▉   ▉   ▉▉▉▉   ▉    ▉      ▉▉▉▉▉▉▉
#▉    ▉  ▉         ▉ ▉             ▉ ▉   ▉    ▉  ▉    ▉       ▉▉▉▉▉
#▉▉▉▉▉▉  ▉▉▉▉▉      ▉               ▉    ▉    ▉  ▉    ▉        ▉▉▉
#▉    ▉  ▉          ▉               ▉    ▉    ▉  ▉    ▉         ▉
#▉    ▉  ▉          ▉   ▉▉▉         ▉    ▉    ▉  ▉    ▉
#▉    ▉  ▉▉▉▉▉▉     ▉   ▉▉▉         ▉     ▉▉▉▉    ▉▉▉▉          ▉
#                        ▉
#                       ▉
#
# You need change the below variables

# Setting the Path to Script Directory
#
# path_to_script_directory is the absolute path to
# the script directory containing run.sh
# THIS IS MANDATORY
#  Change the below string to the correct path ─────────────────────────────┐
#                                                    ┌──────────────────────┴────────────────────┐
path_to_script_directory=${path_to_script_directory:-"PUT THE PROPER SCRIPTS DIRECTORY PATH HERE!"}


# Setting ParFlow installation
#
# ParFlow installation can be set in either one of two ways.
# First: PARFLOW_DIR
# PARFLOW_DIR points to the installation of ParFlow, and contains the
# bin, lib, and include directories.
# Change the below string to the correct path  ─────────┐
#                          ┌────────────────────────────┴────────┐
PARFLOW_DIR=${PARFLOW_DIR:-"PUT THE PROPER PARFLOW_DIR PATH HERE!"}

# Second: module_array
# module_array lists the modules to be loaded in order.
# Spefify the modules that need to be loaded, in the order in which they need to be loaded,
# separated by SPACES into the empty array below, between the parenthesis
#                ┌────────────────────┘
#                ▼
modules_array=(     )
# Valid (as of 4.22.202) example on Ocelote:
# modules_array=(unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi)

# And you're done!

################################################################################
# Nothing below here should be changed unless you know what you're doing.
################################################################################

# Cheeky way of taking in modules_array via qsub -v,
# without oppressive user-facing shenanigans.
if [[ ! -z ${modules_string+x} ]]
then
  modules_array=(${modules_string})
fi

# Check path_to_script_directory
if [[ ${path_to_script_directory} == "PUT THE PROPER SCRIPTS DIRECTORY PATH HERE!" ]]
then
  # Script being executed by PBS, no recourse for finding path_to_script_directory
  if [[ "$0" =~ "/pbs" ]]
  then
    echo "path_to_script_directory HAS NOT BEEN SET PROPERLY."
    echo "path_to_script_directory=${path_to_script_directory}"
    echo "YOU DID NOT FOLLOW THE README OR THE INSTRUCTIONS LISTED HERE."
    echo "SCRIPT IS BEING RUN WITH PBS, AND CANNOT AUTOMAGICALLY DETECT"
    echo "THE PATH TO THE RUN SCRIPT FOR YOU."
    exit

  # Script probably not being executed by PBS.
  # Warn user, but attempt to find path_to_script_directory
  else
    echo "path_to_run_script has not been set properly."
    echo "Currently: path_to_script_directory=${path_to_script_directory}"
    echo "Please read the instructions available both here and in the readme."
    echo "This script will attempt to determine the path to the runscript"

    # Derive possible path from script invocation path
    path_to_script_directory=$(readlink -f $0 | sed "s|test_cases/$(basename $0)|scripts|g")
    # Check possible path
    if [[ ! -d ${path_to_script_directory} ]]
    then
      echo "Could not find path to the scripts directory."
      echo "Please read the instructions available both here and in the readme,"
      echo "and set path_to_run_script properly."
      exit
    fi

    echo "Attempting to use ${path_to_script_directory} as path_to_script_directory."
  fi
fi

# Check PARFLOW_DIR
if [[ ${PARFLOW_DIR} != "PUT THE PROPER PARFLOW_DIR PATH HERE!" ]] && [[ ${PARFLOW_DIR} != "" ]]
then
  # Check PARFLOW_DIR is a directory
  if [[ ! -d ${PARFLOW_DIR} ]]
  then
    echo "PARFLOW_DIR provided but either does not exist or is not a directory: ${PARFLOW_DIR}"
    exit
  fi
  # Upate path with this PARFLOW_DIR's bin, export both.
  PATH=${PARFLOW_DIR}/bin:${PATH}
  export PATH PARFLOW_DIR

# Check modules array
elif [[ ${#modules_array[@]} > 0 ]]
then
  # Load each module in order, checking exit status
  for load_module in ${modules_array[@]}
  do
    module load ${load_module}
    load_exit_code=$?
    # Check successful load
    if [[ ${load_exit_code} != 0 ]]
    then
      echo "Error loading module: ${load_module}"
      echo "Exit code ${load_exit_code}"
      exit
    fi
  done

# Neither method used. Warn, exit.
else
  echo "No method of setting up ParFlow environment was chosen."
  echo "Please read instructions and try again."
  exit
fi

# Sanity check environment
module list
which parflow

# Check for parflow on path
if [[ $(which parflow) == "" ]]
then
  echo "No parflow binary found on path."
  exit -1
fi

# Execute run script
echo "Running: ${size_string}"
${path_to_script_directory}/run.sh ${NP} ${NQ} ${NR} ${NX} ${NY} ${NZ} ${NT} ${test_name}
