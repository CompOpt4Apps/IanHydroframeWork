#!/usr/bin/env bash

# Get path to script as invoked (possible relative)
path_to_script=$(dirname $(readlink -f $0))

# Configurable build settings
build_jobs=8    # Number of parallel build jobs to use
verbose=false   # Print compilation command during build (sets build_jobs to 1). Options: true, false

# Configuration settings
build_type=Release        # Options: Release, Debug
c_flags=""                # Additional C compilation flags
cxx_flags=""              # Additional C++ compilation flags
CLM=ON                    # Enable CLM. Options: ON OFF
amps=mpi1                 # AMPS Layer. Options: seq (maybe?), mpi1 (standard), cuda
timing=true               # Enable timing output. Options: true, false
accelerator_backend=none  # Parallel Accelerator Backend. Options: none, cuda, omp (OpenMP)

# Change some settings if compiling in verbose mode
VERBOSE_arg=""
if [[ "${verbose}" == "true" ]]
then
  VERBOSE_arg="VERBOSE=1"
  build_jobs=1
fi

# Build paths
src_dir="${path_to_script}/parflow"
# Note: These are removed if they already exist.
#       Be careful about modifying their contents,
#       and make sure that they
build_dir="${path_to_script}/_build"
install_dir="${path_to_script}/install"

# log paths
## Path to log file as it is being written to
progressing_build_log_file=${build_dir}/build.log
## Final destination for completed log file
destination_build_log_file=${install_dir}/config/build.log

# Print paths
echo "Build Root: ${path_to_script}"
echo "Source dir: ${src_dir}"
echo "Build dir: ${build_dir}"
echo "Install dir: ${install_dir}"

# Check that source exists
if [[ ! -d ${src_dir} ]]
then
  echo "Source directory does not exist"
  exit
fi

# Remove and re-create build and install directories
[[ -e ${build_dir} ]] && /bin/rm -r ${build_dir}
[[ -e ${install_dir} ]] && /bin/rm -r ${install_dir}
mkdir ${install_dir}
mkdir ${build_dir}

# Set compilation flags
c_flags="${compile_flags}"
cxx_flags="${c_flags}"

# Set CMake command (beware the quoting)
cmake_cmd="cmake ${src_dir}
  -DCMAKE_C_FLAGS=\"${c_flags}\"
  -DCMAKE_CXX_FLAGS=\"${cxx_flags}\"
  -DCMAKE_INSTALL_PREFIX=${install_dir}
  -DPARFLOW_AMPS_LAYER=${amps}
  -DPARFLOW_ACCELERATOR_BACKEND=${accelerator_backend}
  -DPARFLOW_HAVE_CLM=${clm}
  -DCMAKE_BUILD_TYPE=${build_type}
  -DPARFLOW_ENABLE_TIMING=${timing}
  -DPARFLOW_AMPS_SEQUENTIAL_IO=true
"
## Other common configuration settings
## Values of environment variables like <LIB>_BASE should point to the
## root installation directory for <LIB>
# -DCMAKE_C_COMPILER=$(which mpicc)
# -DCMAKE_CXX_COMPILER=$(which mpic++)
# -DCMAKE_LINKER=$(which gcc)
## Hypre Library
# -DPARFLOW_ENABLE_HYPRE=true
# -DHYPRE_ROOT=${HYPRE_BASE}
## SILO library
# -DPARFLOW_ENABLE_SILO=true
# -DSILO_ROOT=${SILO_BASE}


build_cmd="make -j${build_jobs} ${VERBOSE_arg}"
install_cmd="make install"

# Do this in a subshell to capture all output
(
  printf "GIT Remotes:\n"
  (cd ${src_dir} && git remote -v)

  printf "\nGIT Commit and Branch:\n"
  (cd ${src_dir} && git log HEAD^..HEAD --decorate)

  printf "\nCMake Command:\n${cmake_cmd}\n\nBuild Command:\n${build_cmd}\n\nInstall Command:\n${install_cmd}\n"

  cd ${build_dir}
  printf "\nBuild log:\n"

  eval ${cmake_cmd} &&
  eval ${build_cmd} &&
  eval ${install_cmd} &&
  echo "Build Completed Successfully" ||
  echo "Build FAILED!"
) |& tee ${progressing_build_log_file}

# Copy log and cmake cache into install/config for posterity
if [[ -d ${install_dir}/config ]]
then
  cp ${progressing_build_log_file} ${install_dir}/config/.
  cp ${build_dir}/CMakeCache.txt ${install_dir}/config/.
fi
