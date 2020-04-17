# Running on Ocelote

Below is an example script that should work with no additional fiddling.
This example runs a 100x10x5 domain for 2 time-steps on 2 processes (process topology (2,1,1))

```bash
module load unsupported
module load mstrout/parflow/parflow-master-9c0b0f_amps-mpi

NX=100
NY=10
NZ=5

NT=2

NPX=2
NPY=1
NPZ=1

./scripts/run.sh ${NPX} ${NPY} ${NPZ} ${NX} ${NY} ${NZ} ${NT}
```

# Using Alternative Prebuilt ParFlow Modules
You can use any prebuilt ParFlow module you would like.

# Building ParFlow from Scratch

Here is how to build ParFlow from scratch.
These instructions, and the configuration can be adapted to suite your particular needs.

### Dependencies

#### Compilers and Build Tools
+ gcc:
  - version: 7.2.0
  - module: gcc/7.2.0
+ g++
  - version: 7.2.0
  - module: gcc/7.2.0
+ cmake:
  - version: 3.15.2
  - module: mstrout/cmake/3.15.2
  - Notes:
    * This is an 'unsupported' module, see section notes/unsupported for access
+ openmpi:
  - version: gcc/1.10.2
  - module : openmpi/gcc/1.10.2

#### Libraries
+ HDF5
  - version: 1.8.20
  - module: hdf5_18/1.8.20
+ Hyper (openmpi)
  - version: 2.9.0b
  - module: hypre/2/2.9.0b
+ Silo
  - version: 4.10.2
  - module: silo/4/4.10.2

#### Parflow
ParFlow source:
+ git repo:
+ git branch: master
+ git commit: 28ad268e2b0ea44e33cbea8598746429b7477426


## Configuration
cmake configuration options:
```
  -DCMAKE_INSTALL_PREFIX=${PARFLOW_INSTALL_DIRECTORY}
  -DCMAKE_BUILD_TYPE=Release
  -DPARFLOW_AMPS_LAYER=mpi1
  -DPARFLOW_ENABLE_HYPRE=true
  -DHYPRE_ROOT=${HYPRE_BASE}
  -DPARFLOW_ENABLE_HDF5=true
  -DHDF5_ROOT=${HDF5_BASE}
  -DPARFLOW_ENABLE_SILO=true
  -DSILO_ROOT=${SILO_BASE}
  -DPARFLOW_HAVE_CLM=ON
  -DCMAKE_C_COMPILER=$(which gcc)
  -DCMAKE_CXX_COMPILER=$(which g++)
  -DPARFLOW_ENABLE_TIMING=ON
```

### Notes
HYPRE_BASE, HDF5_BASE, and SILO_BASE are set automatically when using the preinstalled modules.
Otherwise, you will need to set these yourself.

ParFlow timing can also be set to OFF if timing is not desired.

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
│   ├── CMakeCache.txt
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
│   ├── CMakeCache.txt
│   ├── CMakeFiles
|   ... more cmake files ...
│   ├── Makefile
│   └── Testing
├── install_directory
│   ├── bin
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


## Installing ParFlow

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
export PARFLOW_COMMIT=28ad268e2b0ea44e33cbea8598746429b7477426

export PARFLOW_AMPS_LAYER=mpi1

# Paths for this project, ParFlow source, build, and install directories
export PARFLOW_ROOT_DIRECTORY=${PWD}/build_tree
export PARFLOW_SOURCE_DIRECTORY=${PARFLOW_ROOT_DIRECTORY}/parflow
export PARFLOW_BUILD_DIRECTORY=${PARFLOW_ROOT_DIRECTORY}/build
export PARFLOW_INSTALL_DIRECTORY=${PARFLOW_ROOT_DIRECTORY}/install

echo PARFLOW_ROOT_DIRECTORY: ${PARFLOW_ROOT_DIRECTORY}
echo PARFLOW_SOURCE_DIR: ${PARFLOW_SOURCE_DIR}
echo PARFLOW_BUILD_DIR: ${PARFLOW_BUILD_DIR}
echo PARFLOW_INSTALL_DIR: ${PARFLOW_INSTALL_DIR}

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
# Load Dependency Modules
##################################################

# Load only necessary modules
# NOTE: Non-ocelote users will need to substitute as necessary

module load unsupported

module load gcc/7.2.0 openmpi/gcc mstrout/cmake/3.15.2 silo hdf5

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
# Configure ParFlow
##################################################

cmake ${PARFLOW_SOURCE_DIRECTORY}                     \
  -DCMAKE_INSTALL_PREFIX=${PARFLOW_INSTALL_DIRECTORY} \
  -DCMAKE_BUILD_TYPE=Release                          \
  -DPARFLOW_AMPS_LAYER=mpi1                           \
  -DPARFLOW_ENABLE_HYPRE=true                         \
  -DHYPRE_ROOT=${HYPRE_BASE}                          \
  -DPARFLOW_ENABLE_HDF5=true                          \
  -DHDF5_ROOT=${HDF5_BASE}                            \
  -DPARFLOW_ENABLE_SILO=true                          \
  -DSILO_ROOT=${SILO_BASE}                            \
  -DPARFLOW_HAVE_CLM=ON                               \
  -DCMAKE_C_COMPILER=$(which gcc)                     \
  -DCMAKE_CXX_COMPILER=$(which g++)                   \
  -DPARFLOW_ENABLE_TIMING=ON


##################################################
# Compile Parflow
##################################################

# Compile ParFlow
make -j${build_jobs}

# Install ParFlow to ${PARFLOW_INSTALL_DIRECTORY}
make install

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

make test
```

# Other notes

## Unsupported Modules
"Unsupported" modules are modules that are not supported by the UA HPC staff.
They are modules that anyone can create.
To enable using unsupported modules run:
`module load unsupported`
From here you can load any of the unsupported modules.
