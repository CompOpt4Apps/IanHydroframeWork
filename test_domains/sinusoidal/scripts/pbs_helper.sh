#!/usr/bin/env bash

# The below variables must exist
# NP
# NQ
# NR
# NX
# NY
# NZ
# NT
# path_to_run_script
# PARFLOW_DIR
# STRINGIFIED_modules_array

if [[ -z ${NP+x} ]]
then
  echo "NP is unset in environment"
  exit
fi

if [[ -z ${NQ+x} ]]
then
  echo "NQ is unset in environment"
  exit
fi

if [[ -z ${NR+x} ]]
then
  echo "NR is unset in environment"
  exit
fi

if [[ -z ${NX+x} ]]
then
  echo "NX is unset in environment"
  exit
fi

if [[ -z ${NY+x} ]]
then
  echo "NY is unset in environment"
  exit
fi

if [[ -z ${NZ+x} ]]
then
  echo "NZ is unset in environment"
  exit
fi

if [[ -z ${NT+x} ]]
then
  echo "NT is unset in environment"
  exit
fi

if [[ -z ${path_to_script_directory+x} ]]
then
  echo "path_to_script_directory is unset in environment"
  exit
fi

if [[ -z ${PARFLOW_DIR+x} ]]
then
  echo "PARFLOW_DIR is unset in environment"
  exit
fi

if [[ -z ${STRINGIFIED_modules_array+x} ]]
then
  echo "STRINGIFIED_modules_array is unset in environment"
  exit
fi

################################################################################
# Everything below here shouldn't be changed unless you know what you're doing.
################################################################################

modules_array=(${STRINGIFIED_modules_array})

if [[ ${path_to_script_directory} == "PUT THE PROPER PATH HERE!" ]]
then
  if [[ "$0" =~ "/pbs" ]]
  then
    echo "path_to_script_directory HAS NOT BEEN SET PROPERLY."
    echo "path_to_script_directory=${path_to_script_directory}"
    echo "YOU DID NOT FOLLOW THE README OR THE INSTRUCTIONS LISTED HERE."
    echo "SCRIPT IS BEING RUN WITH PBS, AND CANNOT AUTOMAGICALLY DETECT"
    echo "THE PATH TO THE RUN SCRIPT FOR YOU."
    exit
  fi

  echo "path_to_run_script has not been set properly."
  echo "Currently: path_to_script_directory=${path_to_script_directory}"
  echo "Please read the instructions available both here and in the readme."
  echo "This script will attempt to determine the path to the runscript"

  path_to_script_directory=${path_to_script_directory:-$(readlink -f $0 | sed "s|test_cases/$(basename $0)|scripts|g")}
  if [[ ! -d ${path_to_script_directory} ]]
  then
    echo "Could not find path to the scripts directory."
    echo "Please read the instructions available both here and in the readme,"
    echo "and set path_to_run_script properly."
    exit
  fi

  echo "Attempting to use ${path_to_script_directory} as path_to_script_directory."
fi

size_string=${NX}x${NY}x${NZ}-${NT}_${NP}-${NQ}-${NR}

if [[ ${PARFLOW_DIR} != "PUT THE PROPER PATH HERE!" ]] && [[ ${PARFLOW_DIR} != "" ]]
then
  if [[ ! -d ${PARFLOW_DIR} ]]
  then
    echo "PARFLOW_DIR provided but either does not exist or is not a directory: ${PARFLOW_DIR}"
    exit
  fi
  PATH=${PARFLOW_DIR}/bin:${PATH}
  export PATH PARFLOW_DIR
elif [[ ${#modules_array[@]} > 0 ]]
then
  for load_module in ${modules_array[@]}
  do
    module load ${load_module}
    load_exit_code=$?
    if [[ ${load_exit_code} != 0 ]]
    then
      echo "Error loading module: ${load_module}"
      echo "Exit code ${load_exit_code}"
      exit
    fi
  done
else
  echo "No method of setting up ParFlow environment was chosen."
  echo "Please read instructions and try again."
  exit
fi

module list
which parflow

if [[ $(which parflow) == "" ]]
then
  echo "No parflow binary found on path."
  exit -1
fi

echo "Running: ${size_string}"
${path_to_script_directory}/run.sh ${NP} ${NQ} ${NR} ${NX} ${NY} ${NZ} ${NT} ocelote_big_sinusoidal_${size_string}
