# Building on UArizona high performance computing systems
There are 3 UA HPC systems:
1. Ocelote (Current system)
2. Puma (Next generation system, slated for soft opening August 2020)
3. El Gato (Previous generation system)

This document details building Parflow and pertinent dependencies on Ocelote and Puma.

# Ocelote
This section discusses some Ocelote specific details that are useful for users developing on the Ocelote system.

## Building ParFlow from Scratch

Here is how to build ParFlow from scratch.
These instructions, and the configuration can be adapted to suite your particular needs.

### Dependencies
This subsection lists tools and libraries needed to build parflow.
This lists versions and Ocelote modules used to build ParFlow on Ocelote.
These are not necessarily the newest/oldest versions compatible with ParFlow.
It is also possible to use alternative installations of these modules, such as locally compiled libraries.

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
    * This is an 'unsupported' module, see subsection Unsupported Modules for access.
+ openmpi:
  - version: gcc/1.10.2
  - module : openmpi/gcc/1.10.2
+ CUDA: (if using the CUDA accelerator ParFlow backend)
  - version CUDA 10.1
  - module: cuda10.0/toolkit/10.0.130

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

#### Parflow Source
ParFlow source:
+ git repo: git@github.com:parflow/parflow.git
+ git branch: master
+ git tag: v3.7.0

### Configuration
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
HYPRE_ROOT=${HYPRE_BASE}
SILO_ROOT=${SILO_BASE}
PARFLOW_ENABLE_SILO=true
```

#### Notes
HYPRE_BASE, HDF5_BASE, and SILO_BASE are set automatically when using the preinstalled modules.
Otherwise, you will need to set these yourself.

ParFlow timing can also be set to OFF if timing is not desired.

`PARFLOW_INSTALL_DIRECTORY` should be an absolute path (for convenience)

#### Example Command
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

### Build
There are no additional options that need to be set for compilation.

#### Example Command
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

#### Notes
To speed up compilation, use the `-j <number of concurrent jobs>` option when calling make.


### Installing ParFlow Locally
To use ParFlow, the environment needs to be setup for it.

#### Setting PARFLOW_DIR variable
The environment variable PARFLOW_DIR needs to be set to the ParFlow install directory.

```bash
export PARFLOW_DIR=${PARFLOW_INSTALL_DIRECTORY}
```

#### Setting Path Variables
The path variables `PATH`, `LIBRARY_PATH`, and `LD_LIBRARY_PATH` must be set to **include** appropriate installation components (`bin` and `lib`).

```bash
export PATH=${PARFLOW_INSTALL_DIRECTORY}/bin:${PATH}
export LIBRARY_PATH=${PARFLOW_INSTALL_DIRECTORY}/lib:${LIBRARY_PATH}
export LD_LIBRARY_PATH=${PARFLOW_INSTALL_DIRECTORY}/lib:${LD_LIBRARY_PATH}
```

### Installing ParFlow as Globally with Module
The Module (modules.readthedocs.io) system.
Dr.Strout's user group has the ability to install 'unsupported' modules.
Module assets (the actual installation) should be located under `/unsupported/mstrout`, and modulefiles (the module definition)should be located under `/unsupported/modulefiles/mstrout`.
These should be mirrored, so that the path to module assets and path to the modulefile are the same.
The name of the module is the path to the modulefiles relative to `/unsupported/modulefiles/` (e.g. a module *named* mstrout/parlfow/latest would have the assets directory `/unsupportedmstrout/parlfow/latest/` and the modulefile `/unsupported/modulefiles/mstrout/parlfow/latest` )

For ParFlow the assets directory is simply the installation directory (e.g. the mstrout/parlfow/latest module would have the structure:
/unsupported/mstrout/parlfow/latest
├── bin
│   └── ... Files under PARFLOW_DIR/bin ...
├── config
│   └── ... Files under PARFLOW_DIR/config ...
└── lib
    └── ... Files under PARFLOW_DIR/lib ...
)

Typically, ParFlow modules are named in the following way:
<GitHub ParFlow Repository Username>/<Git branch>/<Git commit hash or tag>/<compiler>/<compiler version>/<MPI Brand>/<MPI version>/backend-<backend>/amps-<amps layer>/<compilation date>
The assets would be at `/unsupported/mstrout/<GitHub ParFlow Repository Username>/<Git branch>/<Git commit hash or tag>/<compiler>/<compiler version>/<MPI Brand>/<MPI version>/backend-<backend>/amps-<amps layer>/<compilation date>/`
And the modulefile at `/unsupported/modulefiles/mstrout/<GitHub ParFlow Repository Username>/<Git branch>/<Git commit hash or tag>/<compiler>/<compiler version>/<MPI Brand>/<MPI version>/backend-<backend>/amps-<amps layer>/<compilation date>`

Below is a template of a modulefile.
```tcl
#%Module -*- tcl -*-
###example
### modulefile
###

# Typical root location of ParFlow installation
set parflow_modules_root   /unsupported/mstrout/parflow
# ParFlow module name
set parflow_module_version_path parflow/<GitHub ParFlow Repository Username>/<Git branch>/<Git commit hash or tag>/<compiler>/<compiler version>/<MPI Brand>/<MPI version>/backend-<backend>/amps-<amps layer>/<compilation date>
# Dependencies (modules) for this module
set module_dependencies [list autotools cmake/3.15.4 gnu8/8.3.0 python/3.8 openmpi3/3.1.4 hdf5/1.10.5 silo/4.10.2 hypre/2.11.2]

set whatis_message "Adds Parflow to your environment"
set name "Parflow"
set version "$parflow_module_version_path"

proc ModulesHelp { } {
  puts stderr "\t$whatis_message"
}

module-whatis $whatis_message
module-whatis "Name: $name"
module-whatis "Version: $version"

set            PARFLOW_BASE      [ file join $parflow_modules_root $parflow_module_version_path ]
setenv         PARFLOW_BASE      $PARFLOW_BASE
setenv         PARFLOW_DIR       $PARFLOW_BASE
prepend-path   PATH              [ file join $PARFLOW_BASE bin]

set            lib_path          [ file join $PARFLOW_BASE lib ]
prepend-path   LD_LIBRARY_PATH   $lib_path
prepend-path   LIBRARY_PATH      $lib_path

set            include_path      [ file join $PARFLOW_BASE include ]
prepend-path   CPATH             [ file join $PARFLOW_BASE include ]

# Note: *FLAGS variables (such as LDFLAGS, CFLAGS, CPPFLAGS) are not set here
#       as these paths fill the role of adding '-I' and '-L' flags by default.

# Prerequisites
if { [ module-info mode load ] } {
  foreach dependency $module_dependencies {
    if { ! [ is-loaded $dependency ] } {
      module load $dependency
    }
  }
}

# Logging (from:ianbertolacci I'm not sure what this is, I assume it's logging)
set myMode [ module-info mode ]
set exitflag [catch { exec /usr/bin/id -un } userName]
set curMod  [module-info name]
exec /bin/logger -i -p local4.info -t modulecmd $userName: module $myMode $curMod
```


### Example Complete Build Script
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
# Load Dependency Modules
##################################################

# Load only necessary modules
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

  # Log loaded modules
  printf "\nModules:\n"
  module list

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

## Other Notes

###Unsupported Modules
"Unsupported" modules are modules that are not supported by the UA HPC staff.
They are modules that anyone can create.
To enable using unsupported modules run:
`module load unsupported`
From here you can load any of the unsupported modules.
