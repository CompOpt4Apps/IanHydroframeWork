# Building ParFlow from Scratch

Here is how to build ParFlow from scratch.
These instructions, and the configuration can be adapted to suite your particular needs.

The script (build.sh)[infrastructure/build/build.sh] is a slightly simplified and maybe more documented version of the build scripts I eventually started using for my builds.

## Dependencies
This subsection lists tools and libraries needed to build parflow.
This lists versions and Ocelote modules used to build ParFlow on Ocelote.
These are not necessarily the newest/oldest versions compatible with ParFlow.
It is also possible to use alternative installations of these modules, such as locally compiled libraries.

### Compilers and Build Tools
+ gcc:
  - version: 7.2.0
+ g++
  - version: 7.2.0
+ cmake:
  - version: 3.15.2
+ openmpi:
  - version:1.10.2
+ CUDA: (if using the CUDA accelerator ParFlow backend)
  - version CUDA 10.1

### Libraries
+ HDF5 (Optional)
  - version: 1.8.20
  - Notes:
    * Set HDF5_BASE environment variable to library installation.
+ Hyper (Optional)
  - version: 2.9.0
  - Notes:
    * Set HYPRE_BASE environment variable to library installation.
+ Silo (Optional)
  - version: 4.10.2
  - Notes:
    * Set SILO_BASE environment variable to library installation.

### Parflow Source
ParFlow source:
+ git repo: git@github.com:parflow/parflow.git
+ git branch: master
+ git tag: v3.7.0

## Configuration
Typical CMake configuration options (prefix with `-D`)
```
CMAKE_INSTALL_PREFIX=${PARFLOW_INSTALL_DIRECTORY}
CMAKE_BUILD_TYPE=Release
CMAKE_C_COMPILER=$(which mpicc)
CMAKE_CXX_COMPILER=$(which mpic++)
CMAKE_C_FLAGS=\"${c_flags}\"
CMAKE_CXX_FLAGS=\"${cxx_flags}\"
PARFLOW_AMPS_LAYER=${PARFLOW_AMPS_LAYER}
PARFLOW_ENABLE_TIMING=true
PARFLOW_AMPS_SEQUENTIAL_IO=true
PARFLOW_HAVE_CLM=ON
```

These are also common configuration options:
```
PARFLOW_ENABLE_HYPRE=true
HYPRE_ROOT=${HYPRE_BASE}
PARFLOW_ENABLE_SILO=true
SILO_ROOT=${SILO_BASE}
```

### Notes
Ensure HYPRE_BASE, HDF5_BASE, and SILO_BASE environment variables are set.
Otherwise, you will need to set these yourself.

ParFlow timing can also be set to OFF if timing is not desired.
HDF5, Hyper, and Silo can be disabled (PARFLOW_ENABLE_<library>=false)
CLM can also be disabled (PARFLOW_HAVE_CLM=OFF)

`PARFLOW_INSTALL_DIRECTORY` should be an absolute path (for convenience)

### Example Command
Assume the following directory structure
```
build_tree
└── parflow
    ├── acmacros
    ├── bin
    ... more parflow source files ...
    ├── user_manual.pdf
    └── VERSION
```

```bash
BUILD_DIRECTORY=${PWD}/build_directory
PARFLOW_INSTALL_DIRECTORY=${PWD}/install_directory
PARFLOW_SOURCE_DIRECTORY=${PWD}/parflow

mkdir ${BUILD_DIRECTORY}
cd ${BUILD_DIRECTORY}
cmake ${PARFLOW_SOURCE_DIRECTORY} ${CMAKE_CONFIGURATION_OPTIONS}
```

## Build
There are no additional options that need to be set for compilation.

### Example Command
Assume the following directory structure

```
build_tree
├── build_directory
│   ├── CMakeCache.txt
│   ├── CMakeFiles
|   ... more cmake files ...
│   ├── Makefile
│   └── Testing
└── parflow
      ├── acmacros
      ├── bin
      ... more parflow source files ...
      ├── user_manual.pdf
      └── VERSION
```

```bash
cd ${BUILD_DIRECTORY}
make install
```

This will build ParFlow and install it to the location defined by `PARFLOW_INSTALL_DIRECTORY`:

```
build_tree
├── build_directory
│   ├── CMakeCache.txt
│   ├── CMakeFiles
|   ... more cmake files ...
│   ├── Makefile
│   └── Testing
├── install_directory
│   ├── bin
│   ├── config
|   └── lib
└── parflow
      ├── acmacros
      ├── bin
      ... more parflow source files ...
      ├── user_manual.pdf
      └── VERSION
```

### Notes
To speed up compilation, use the `-j <number of concurrent jobs>` option when calling make.


## Installing ParFlow Locally
To use ParFlow, the environment needs to be setup for it.

### Setting PARFLOW_DIR variable
The environment variable PARFLOW_DIR needs to be set to the ParFlow install directory.

```bash
export PARFLOW_DIR=${PARFLOW_INSTALL_DIRECTORY}
```

### Setting Path Variables
The path variables `PATH`, `LIBRARY_PATH`, and `LD_LIBRARY_PATH` must be set to **include** appropriate installation components (`bin` and `lib`).

```bash
export PATH=${PARFLOW_INSTALL_DIRECTORY}/bin:${PATH}
export LIBRARY_PATH=${PARFLOW_INSTALL_DIRECTORY}/lib:${LIBRARY_PATH}
export LD_LIBRARY_PATH=${PARFLOW_INSTALL_DIRECTORY}/lib:${LD_LIBRARY_PATH}
```

## Example Complete Build Script
Below is a build script which should build ParFlow exactly as described above, including loading modules, downloading and checking out specific ParFlow source, configuring, building, and installing.

In addition, it also logs the whole build, including git state and stores it into PARFLOW_DIR/config/build.log

Please be aware of any configurations your shell environment may have.

```bash
##################################################
# Setup Build Configuration and Environment
##################################################

# Number of make build jobs (set to 1 for serial builds)
export build_jobs=28

# ParFlow source and version
export PARFLOW_REMOTE=git@github.com:ParFlow/ParFlow.git
export PARFLOW_BRANCH=master
export PARFLOW_COMMIT=v3.7.0
#Note: this is a tag, but could also be a commit hash.
# Git checkout is invoked the same way regardless of the type.

export PARFLOW_AMPS_LAYER=mpi1

# Paths for this project, ParFlow source, build, and install directories
export PARFLOW_ROOT_DIRECTORY=${PWD}/build_tree
export PARFLOW_SOURCE_DIRECTORY=${PARFLOW_ROOT_DIRECTORY}/parflow
export PARFLOW_BUILD_DIRECTORY=${PARFLOW_ROOT_DIRECTORY}/build
export PARFLOW_INSTALL_DIRECTORY=${PARFLOW_ROOT_DIRECTORY}/install

echo PARFLOW_ROOT_DIRECTORY: ${PARFLOW_ROOT_DIRECTORY}
echo PARFLOW_SOURCE_DIRECTORY: ${PARFLOW_SOURCE_DIRECTORY}
echo PARFLOW_BUILD_DIRECTORY: ${PARFLOW_BUILD_DIRECTORY}
echo PARFLOW_INSTALL_DIRECTORY: ${PARFLOW_INSTALL_DIRECTORY}

echo PARFLOW_REMOTE: ${PARFLOW_REMOTE}
echo PARFLOW_BRANCH: ${PARFLOW_BRANCH}
echo PARFLOW_COMMIT: ${PARFLOW_COMMIT}

echo PARFLOW_AMPS_LAYER: ${PARFLOW_AMPS_LAYER}

##################################################
# Setup Build Tree
##################################################

# check for previous builds
if [[ -e ${PARFLOW_ROOT_DIRECTORY} ]]
then
  echo "ParFlow root already exists! (${PARFLOW_ROOT_DIRECTORY})"
  exit
fi

# Create non-source directories
mkdir ${PARFLOW_ROOT_DIRECTORY}
mkdir ${PARFLOW_BUILD_DIRECTORY} ${PARFLOW_INSTALL_DIRECTORY}

##################################################
# Build ParFlow
##################################################

# Go into ParFlow tree
cd ${PARFLOW_ROOT_DIRECTORY}

##################################################
# Checkout ParFlow Source and Version
##################################################

# Clone specified ParFlow source
git clone ${PARFLOW_REMOTE} ${PARFLOW_SOURCE_DIRECTORY}
cd ${PARFLOW_SOURCE_DIRECTORY}
# Checkout specified branch
git checkout ${PARFLOW_BRANCH}
# Checkout specified commit
git checkout ${PARFLOW_COMMIT}

# Go into ParFlow build directory
cd ${PARFLOW_BUILD_DIRECTORY}


##################################################
# Preparing Build, Configure, and Install ParFlow Commands
##################################################

# Any build flags that are needed.
c_flags=""
cxx_flags="${c_flags}"

# Configure command (using cmake)
cmake_cmd="cmake ${PARFLOW_SOURCE_DIRECTORY}
  -DCMAKE_INSTALL_PREFIX=${PARFLOW_INSTALL_DIRECTORY}
  -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_C_COMPILER=$(which mpicc)
  -DCMAKE_CXX_COMPILER=$(which mpic++)
  -DCMAKE_C_FLAGS=\"${c_flags}\"
  -DCMAKE_CXX_FLAGS=\"${cxx_flags}\"
  -DPARFLOW_AMPS_LAYER=${PARFLOW_AMPS_LAYER}
  -DPARFLOW_ENABLE_TIMING=true
  -DPARFLOW_AMPS_SEQUENTIAL_IO=true
  -DPARFLOW_HAVE_CLM=ON
  -DHYPRE_ROOT=${HYPRE_BASE}
  -DSILO_ROOT=${SILO_BASE}
  -DPARFLOW_ENABLE_SILO=true
"

# Build command (using make)
build_cmd="make -j${build_jobs}"

# Install command (using make)
install_cmd="make install"

##################################################
# Executing Build, Configure, and Install ParFlow Commands
##################################################

build_log_file="${PARFLOW_BUILD_DIRECTORY}/build.log"
# Do this in a subshell to capture all output
(
  # Logging
  # Log git information
  printf "GIT Remotes:\n"
  (cd ${PARFLOW_SOURCE_DIRECTORY} && git remote -v)

  printf "\nGIT Commit and Branch:\n"
  (cd ${PARFLOW_SOURCE_DIRECTORY} && git log HEAD^..HEAD --decorate)

  # Log configure, build, and install commands
  printf "\nCMake Command:\n${cmake_cmd}\n\nBuild Command:\n${build_cmd}\n\nInstall Command:\n${install_cmd}\n"

  # Perform build
  cd ${PARFLOW_BUILD_DIRECTORY}
  printf "\nBuild log:\n"

  eval ${cmake_cmd} &&
  eval ${build_cmd} &&
  eval ${install_cmd} &&
  echo "Build Completed Successfully" ||
  echo "Build FAILED!"
) |& tee ${build_log_file}

# Move log to PARFLOW_DIR/config/.
if [[ -d ${PARFLOW_INSTALL_DIRECTORY}/config ]]
then  
  cp ${build_log_file} ${PARFLOW_INSTALL_DIRECTORY}/config/.
fi

##################################################
# Setup ParFlow Installation Environment
##################################################

export PARFLOW_DIR=${PARFLOW_INSTALL_DIRECTORY}
export PATH=${PARFLOW_INSTALL_DIRECTORY}/bin:${PATH}
export LIBRARY_PATH=${PARFLOW_INSTALL_DIRECTORY}/lib:${LIBRARY_PATH}
export LD_LIBRARY_PATH=${PARFLOW_INSTALL_DIRECTORY}/lib:${LD_LIBRARY_PATH}

##################################################
# Run ParFlow Tests (optional but recommended)
##################################################

cd ${PARFLOW_BUILD_DIRECTORY} && make test
```
