#!/usr/bin/env bash

# Print output of parflow run (usually set to true)
print_output_text=true

# Print timing CSV file (usually set to true)
print_timing_csv=true

# Print kinsol log (usually set to false)
print_kinsol_log=false

# Print parflow log (usually set to false)
print_output_log=false

# Redirect all stderr from run command to stdout (usually true)
stderr_to_stdout=true
# Note: most time tools emmit their data to stderr.
# Note: that the parflow run performs it's own redirection which I will not attempt to describe here.

time_cmd="/usr/bin/time -v"

# ======================================
# Do not change anything below this line
# ======================================

# Test specific information
test_name="Sinusoidal"
default_run_name_prefix="unnamed_${test_name}"
test_tcl_script_name="sinusoidal.tcl"
timestamp="$(date +%m-%d_%H:%M:%S)"
seperator_string="==================================================="

# Possible values: copy, link
move_asset_mode="link"
# Use copy if assets may be written to or filesystem being executed under is
# remote from assets (such as a network mounted FS)
# Use linked otherwise, as the reduces the amount of disk space
# each test invocation occupies.

useage_message="Runner script for ${test_name}\nUsage: ${0} <Processes in P> <Processes in Q> <Processes in R> <Size in X> <Size in Y> <Size in Z> <Timesteps> [run-name]\nrun-name: Name used to identify this test run. Defaults to ${default_run_name_prefix}_proc-<Processes in P>-<Processes in Q>-<Processes in R>_size-<Size in X>x<Size in Y>x<Size in Z>_time-<Timesteps>_<time-stamp>"

# test setup

# Print Usage information
if [[ $# < 7 || $# > 8 ]]
then
  echo -e ${useage_message}
  exit
fi

# Number of processes in each direction
NP=${1}
NQ=${2}
NR=${3}

# Size in each direction
NX=${4}
NY=${5}
NZ=${6}

#timesteps
NT=${7}

# Create a run_name with prefix
if [[ $# == 7 ]]
then
  run_name_prefix=${default_run_name_prefix}
else
  run_name_prefix=${8}
fi

run_name="${run_name_prefix}_proc-${NP}-${NQ}-${NR}_size-${NX}x${NY}x${NZ}_time-${NT}_${timestamp}"

if [[ "$(which parflow)" == "" ]]
then
  echo "No parflow found in environment"
  exit
fi

path_prefix () {
  base_name=$(basename -- "$1")
  prefix_path=$(echo "$1" | sed -r "s|/?${base_name}||g" )
  echo $prefix_path
  unset base_name prefix_path
}

# Get path to script as invoked (possible relative)
path_to_script=$(path_prefix $0)

# Create absolute path if necessary
if [[ ${path_to_script} != /* ]]
then
  path_to_script=${PWD}/${path_to_script}
fi

# Derive this test's paths for the directory hierchy
# Derived by knowing that the path to the script is in "scripts"
# so "${path_to_script}/.." is the root of the tests
test_root_path="${path_to_script}/.."
output_root_path="${test_root_path}/outputs"
scripts_path="${test_root_path}/scripts"
test_files_path="${test_root_path}/assets"
run_output_path=${output_root_path}/${run_name}

echo "Run Name: ${run_name}"
echo "Test Root Path: ${test_root_path}"
echo "Output Path: ${output_root_path}"
echo "Test Scripts Path: ${scripts_path}"
echo "Test Files Path: ${test_files_path}"
echo "Run Output Path: ${run_output_path}"

if [[ ! -e "${test_root_path}" ]]
then
  echo "Unable to derive proper path to test directory root: ${test_root_path}"
  exit
fi

if [[ ! -e "${scripts_path}" ]]
then
  echo "Unable to derive proper path to test directory root: ${scripts_path}"
  exit
fi

# Create ouptut directory hieriarcy
# If no root output directory exists, create it
if [[ ! -e "${output_root_path}" ]]
then
  mkdir ${output_root_path}
fi

# Create this run's output directory
mkdir ${run_output_path}

# Setup convinience links at root level
# Unlink previous last_output link
if [ -L ${test_root_path}/last_output ]
then
  unlink ${test_root_path}/last_output
fi

# Create new link to run's output
ln -s ${run_output_path} ${test_root_path}/last_output

# Setup files and run test in run's output directory
cd ${run_output_path}
pwd

# Copy or link all assets to run directory
if [[ ${move_asset_mode} == "copy" ]]
then
  cp -r ${test_files_path}/* .
elif [[ ${move_asset_mode} == "link" ]]
then
  for f in ${test_files_path}/*;
  do
    ln -s $f
  done
fi

# Run test
run_command="${time_cmd} tclsh ${test_tcl_script_name} ${NP} ${NQ} ${NR} ${NX} ${NY} ${NZ} ${NT} ${run_name}"
echo "Running: ${run_command}"
if [[ ${stderr_to_stdout} == "true" ]]
then
  ${run_command} 2>&1
else
  ${run_command}
fi

# Output logs
# stdout log
if [[ ${print_output_text} == "true" ]]
then
  echo ${seperator_string}
  echo "Output Log File"
  if [ -e "${run_name}.out.txt" ]
  then
    cat ${run_name}.out.txt
  else
    echo "No stdout file"
  fi
fi

# Kinsol log
if [[ ${print_kinsol_log} == "true" ]]
then
  echo ${seperator_string}
  echo "Kinsol Log File"
  if [ -e "${run_name}.out.kinsol.log" ]
  then
    cat ${run_name}.out.kinsol.log
  else
    echo "No kinsol log file"
  fi
fi

# Timing log
if [[ ${print_timing_csv} == "true" ]]
then
  echo ${seperator_string}
  echo "Timing Log File"
  if [ -e "${run_name}.out.timing.csv" ]
  then
    cat ${run_name}.out.timing.csv
  else
    echo "No timing log file"
  fi
fi

echo ${seperator_string}

if [[ ${print_output_log} == "true" ]]
then
  echo ${seperator_string}
  echo "Parflow Output Log File"
  if [ -e "${run_name}.out.log" ]
  then
    cat ${run_name}.out.log
  else
    echo "No log"
  fi
fi
