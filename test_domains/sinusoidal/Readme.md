# Sinusoidal Test Case
Sinusoidal is a test case for exploring performance across arbitrary
domain sizes.
This test case was adapted from the pfp4 test case from Stefan Kollet, and
was described as a weak scaling with periodic boundary condition.

This includes both a nice runner script (`./scripts/run.sh`) which manages inputs/outputs and invocation of the test, as well as the underlying tcl script (`./assets/sinusoidal.tcl`) which performs the actual ParFlow execution.
Using the runner script is preferred.

By default, the runner script test prints out the ParFlow standard output, and timing information from `/usr/bin/time` and ParFlow's internal timing system (if it has been built with timing configured to on, see section on building ParFlow).
Output files are managed by the runner script.
Output files from a run can be found in `outputs`.
In `outputs/`, each test run has its own directory named as  `<test_name>_<time_stamp_of_test_invocation>`.
For convenience, `last_output` links to the output directory from the most recent run.

This Readme is very comprehensive, discussing how to execute the run script, the tcl script (unprefered); shows all usage arguments for both scripts; discusses all test cases, their parameterization, previous metric observation (if pertinent), and background commentary; and the setting up and execution of the PBS test cases.
Fully copy-and-pasteable code examples are shown throughout the readme, and the last section "100% Complete, Clone to Run examples" shows (as the name suggests) several complete examples starting from cloning the repository, to editing scripts (if necessary), to running the test case and viewing output.

Be aware that some of this discussion has details specific to the UArizona HPC system, Ocelote.
This is the case for any discussion of modules that arise, primarily from the discussion of PBS script modification and execution.
However, there are *more* Ocelote specific details in the `Ocelote_Readme.md` document.
In there, existing ParFlow modules are listed and Ocelote specific ParFlow build instructions are given.

## How To Read This Document
This readme makes extensive use of the Markdown format (github flavored).
Worth mentioning is code blocks, which appear like this:

```language
code text
```
(aka  
\`\`\`language  
code text  
\`\`\`  
for our those reading on github or a Markdown renderer)

the triple tics indicates a code block and the `language` tag indicates the language the code block is written in.
The `language` tag is not part of the code in the code block.

To show output as it would appear in a terminal, comment blocks denote the beginning and end of a command's output.
This allows you to copy and execute the entirety of a Bash shell block without having to format, edit, or remove the output.
```bash
echo "Hello World! This ends up as output on the terminal, and will be put into fancy blocks."
################################################################################
# BEGIN output from `echo "This is output to the terminal"`
################################################################################
# Hello World! This ends up as output on the terminal, and will be put into fancy blocks.
################################################################################
# END output from `echo "This is output to the terminal"`
################################################################################
```

# Run Script
The run script (`scripts/run.sh`) is the preferred method of running the sinusoidal domain.
The run script manages running the underlying sinudoidal tcl script (described in another section), the output files, timeing, and printing of results.

By default, the runner script test prints out the ParFlow standard output, and timing information from `/usr/bin/time` and ParFlow's internal timing system (if it has been built with timing configured to on, see section on building ParFlow).
Output files from a run can be found in `outputs`.
In `outputs`, each test run has its own directory named as  `<test_name>_<time_stamp_of_test_invocation>`.
For convenience, `last_output` links to the output directory from the most recent run.

## Script Arguments
Both the bash run-script and the tcl test scrip accepts the following parameters in this order:
+ Processes in X
  - Number of processes executing^ in X dimension.
+ Processes in Y
  - Number of processes executing^ in Y dimension.
+ Processes in Z
  - Number of processes executing^ in Z dimension.
+ Size in X
  - Number of cells in the X dimension.
+ Size in Y
  - Number of cells in the Y dimension.
+ Size in Z
  - Number of cells in the Z dimension.
+ Time steps
  - Number of time steps to simulate.
+ Test Name (optional)
  - Name used to prefix folders and files produced by this test
  - Default: unnamed_Sinusoidal
  - This becomes part of a path so do not used spaces or special characters other than any of the following: : - _ .

^For the process topology, the total number of processes executing is the
product of the processes in each dimension (i.e. for *any* topolgy using any permutation of 2, 3, and 4, the total number of processes is 24 (2 x 3 x 4))

## Internal Script Configurations
The run script has several internal configuration settings that can be changed
as desired.
+ print_output_text
  - Bool string ("true" / "false" )
  - Prints output from ParFlow when "true"
  - Default: true
+ print_timing_csv
  - Bool string ("true" / "false" )
  - Prints ParFlow timing csv when "true"
  - Ideally ParFlow build has been configured with `-DParFlow_ENABLE_TIMING=true`
  - Default: true
+ print_kinsol_log
  - Bool string ("true" / "false" )
  - Prints ParFlow kinsol log when "true"
  - Default: false
+ print_output_log
  - Bool string ("true" / "false" )
  - Prints ParFlow output log when "true"
  - Default: false
+ stderr_to_stdout
  - Bool string ("true" / "false" )
  - Redirects all stderr output from run command to stdout when "true"
  - Default: true
+ time_cmd
  - bash expression string
  - Default is "/usr/bin/time -v"
  - Can also be empty string if no timing is desired.

## Example Usage of Run Script

Here is a demonstration of using the sinusoidal test domain, as defined in the Hello World script test case (`test_cases/hello_world.sh`).
```bash
cat ./test_cases/hello_world.sh
################################################################################
# BEGIN output from `cat ./test_cases/hello_world.sh`
################################################################################
# #!/usr/bin/env bash
# test_name=hello_world
#
# #set number of cells
# number_cells_X=10
# number_cells_Y=100
# number_cells_Z=20
#
# # Run for 24 hours
# number_timesteps=24
#
# # 8 processes, making 4 partitions in the X dimension, and 2 in the Y.
# number_processes_X=4
# number_processes_Y=2
# number_processes_Z=1
#
# # Create path to actual run script
# # Change if moving script somewhere other than test_domains/sinusoidal/examples
# path_to_scripts=${path_to_scripts:-$(readlink -f $0 | sed "s|test_cases/$(basename $0)|scripts|g")}
#
# # Invoke run script
# #   Process topology, X Y Z
# #   Grid layout, X Y Z
# #   Timesteps
# #   Test Name
# ${path_to_scripts}/run.sh \
#   ${number_processes_X} ${number_processes_Y} ${number_processes_Z} \
#   ${number_cells_X}     ${number_cells_Y}     ${number_cells_Z} \
#   ${number_timesteps} \
#   ${test_name}
################################################################################
# END output from `cat ./test_cases/hello_world.sh`
################################################################################

./test_cases/hello_world.sh
################################################################################
# BEGIN output from `./test_cases/hello_world.sh`
################################################################################
# Run Name: hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
# Test Root Path: path/to/repo/test_domains/sinusoidal/scripts/..
# Output Path: path/to/repo/test_domains/sinusoidal/scripts/../outputs
# Test Scripts Path: path/to/repo/test_domains/sinusoidal/scripts/../scripts
# Test Files Path: path/to/repo/test_domains/sinusoidal/scripts/../assets
# Run Output Path: path/to/repo/test_domains/sinusoidal/scripts/../outputs/hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
# path/to/repo/test_domains/sinusoidal/outputs/hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
# Running: /usr/bin/time -v tclsh sinusoidal.tcl 4 2 1 100 200 10 24 hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
#
# 	Command being timed: "tclsh sinusoidal.tcl 4 2 1 100 200 10 24 hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34"
# 	User time (seconds): 21.56
# 	System time (seconds): 2.55
# 	Percent of CPU this job got: 345%
# 	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:06.98
# 	Average shared text size (kbytes): 0
# 	Average unshared data size (kbytes): 0
# 	Average stack size (kbytes): 0
# 	Average total size (kbytes): 0
# 	Maximum resident set size (kbytes): 57016
# 	Average resident set size (kbytes): 0
# 	Major (requiring I/O) page faults: 29
# 	Minor (reclaiming a frame) page faults: 87045
# 	Voluntary context switches: 7551
# 	Involuntary context switches: 1364049
# 	Swaps: 0
# 	File system inputs: 0
# 	File system outputs: 46664
# 	Socket messages sent: 0
# 	Socket messages received: 0
# 	Signals delivered: 0
# 	Page size (bytes): 4096
# 	Exit status: 0
# ===================================================
# Output Log File
# Node 0: Using process grid (4,2,1)
# Node 0: Well Information
# Node 0: No Wells.
# Node 0: Well Information
# Node 0: No Wells.
# Node 0: Problem solved
# ===================================================
# Timing Log File
# Timer,Time (s),MFLOPS (mops/s),FLOP (op)
# Solver Setup,0.455600,0.000000,0
# Solver,5.829700,3.293484,1.92e+07
# Solver Cleanup,0.020300,0.000000,0
# Matvec,0.000000,0.000000,0
# PFSB I/O,0.000000,0.000000,0
# PFB I/O,0.000000,0.000000,0
# CLM,0.226000,0.000000,0
# PFSOL Read,0.000000,0.000000,0
# Clustering,1.923100,0.000000,0
# Permeability Face,0.000000,0.000000,0
# Godunov Advection,0.000000,0.000000,0
# Geometries,1.114100,0.000000,0
# SubsrfSim,0.074000,0.000000,0
# Porosity,0.001100,0.000000,0
# PhaseRelPerm,0.696100,0.000034,24
# PFMG,0.000000,0.000000,0
# HYPRE_Copies,0.000000,0.000000,0
# NL_F_Eval,2.486300,0.000010,24
# KINSol,3.032900,6.330583,1.92e+07
# Total Runtime,6.298500,-nan,0
# ===================================================
################################################################################
# END output from `./test_cases/hello_world.sh`
################################################################################
```


# TCL Script
The tcl script `assets/sinusoida.tcl` is what sets up the ParFlow database and executes ParFlow.
It can be used directly, but in larger processes (such performance data-collection) requires manual management of the output.
This management is precisely why the run script exists.

## Example Using the TCL script

```bash
# Make directory for collecting test outputs.
# This is one of the things managed by the run script.
mkdir manual_sinusoidal

cd manual_sinusoidal

# Just to show that there's nothing in here.
ls
################################################################################
# BEGIN output from `ls`
################################################################################
################################################################################
# END output from `ls`
################################################################################

test_name=hello_world

#set number of cells
number_cells_X=10
number_cells_Y=100
number_cells_Z=20

# Run for 24 hours
number_timesteps=24

# 8 processes, making 4 partitions in the X dimension, and 2 in the Y.
number_processes_X=4
number_processes_Y=2
number_processes_Z=1

# Invoke tcl script
#   Process topology, X Y Z
#   Grid layout, X Y Z
#   Timesteps
#   Test Name
tclsh ../assets/sinusoidal.tcl \
  ${number_processes_X} ${number_processes_Y} ${number_processes_Z} \
  ${number_cells_X}     ${number_cells_Y}     ${number_cells_Z} \
  ${number_timesteps} \
  ${test_name}

# There is no output from.
# Printing the results when the script has is also handled by the run script.
# There is also now timing command output, though aspects of the
# *timing.csv and *.out.log could make up for that, but are also present
# anyway when using the run script.

# But there are quite a few output
ls
################################################################################
# BEGIN output from `ls`
################################################################################
# hello_world.out.kinsol.log
# hello_world.out.log
# hello_world.out.pfmetadata
# hello_world.out.pftcl
# hello_world.out.timing.csv
# hello_world.out.txt
# hello_world.pfidb
################################################################################
# END output from `ls`
################################################################################

```

## Script Arguments
Both the bash run-script and the tcl test scrip accepts the following parameters in this order:
+ Processes in X
  - Number of processes executing^ in X dimension.
+ Processes in Y
  - Number of processes executing^ in Y dimension.
+ Processes in Z
  - Number of processes executing^ in Z dimension.
+ Size in X
  - Number of cells in the X dimension.
+ Size in Y
  - Number of cells in the Y dimension.
+ Size in Z
  - Number of cells in the Z dimension.
+ Time steps
  - Number of time steps to simulate.
+ Test Name (optional)
  - Name used to prefix folders and files produced by this test
  - Default: sinusoidal.cpu
  - This becomes part of a path so do not used spaces or special characters other than any of the following: : - _ .

^For the process topology, the total number of processes executing is the
product of the processes in each dimension (i.e. for *any* topolgy using any permutation of 2, 3, and 4, the total number of processes is 24 (2 x 3 x 4))

## Other Notes

### Dump interval
The tcl script is configured to only dump simulation state on the last time-step of the run.

# Test Cases
There are several specific test cases using the sinusoidal domain.

## Hello World Script
This is a Bash script that shows how to run a domain using the run script.

* File: `test_cases/hello_world.sh`
* Sinusoidal Parameters:
  + NP: 4
  + NQ: 2
  + NR: 1
  + NX: 100
  + NY: 200
  + NZ: 10
  + NT: 24

## Hello World PBS Script
This is a PBS script that shows how to run a domain using the run script in the context of PBS.
It is meant to be a template for building and running other PBS test cases.
Unless otherwise mentioned, all PBS test cases are run in the same way this test case is run, and so all PBS tutorials in this readme use this test case.

* File: `test_cases/hello_world.pbs`
* Sinusoidal Parameters:
  + NP: 4
  + NQ: 2
  + NR: 1
  + NX: 100
  + NY: 200
  + NZ: 10
  + NT: 24
* PBS Settings:
  + 1 Node, 1 CPU, 6GB/core, 6GB memory total.
    - `-l select=1:ncpus=1:mem=6gb:pcmem=6gb`
  + Standard queue
    - `-q standard`
  + Job name: `hello_world_b`
    - `-N hello_world_pbs`
  + Group: mstroupt
    - `-W group_list=mstrout`
  + Shared node placement
    - `-l place=pack:shared`
  + 5 minutes of wall clock runtime
    - `-l walltime=00:05:00`
  + Both stdout and stderr to same file
    - `-j oe`

## Large Squarish
This test cases is designed to have a peak memory footprint near 168GB.
This test case has NX and NY parameters that are roughly equal (4.27% off-square).
It was designed for running on the UArizona HPC system Ocelote.

* File: `test_cases/large_squarish.pbs`
* Sinusoidal Parameters:
  + NP: 1
  + NQ: 1
  + NR: 1
  + NX: 5000
  + NY: 5223
  + NZ: 5
  + NT: 2
* PBS Settings:
  + 1 Node, 28 CPUs, 6GB/core, 168GB memory total.
    - `-l select=1:ncpus=28:mem=168gb:pcmem=6gb`
  + Standard queue
    - `-q standard`
  + Job name: `hello_world_b`
    - `-N large_squarish_ocelote_big_sinusoidal`
  + Group: mstroupt
    - `-W group_list=mstrout`
  + Exclusive node placement
    - `-l place=pack:exclhost`
  + 1 hour of wall clock runtime
    - `-l walltime=1:00:00`
  + Both stdout and stderr to same file
    - `-j oe`
* Observed metrics:
  + Memory Occupation: 170666612 KB
  + Runtime: 2002.57 seconds


### Background
This test case has parameters chosen such that a test fills the memory of a standard, non-GPU node.
The configuration of Ocelote nodes can be found [here](https://public.confluence.arizona.edu/display/UAHPC/Compute+Resources) ([archived 4.22.2020](https://web.archive.org/web/20200423043707/https://public.confluence.arizona.edu/display/UAHPC/Compute+Resources)).
While Ocelote nodes have 192 GB of RAM, the recommended maximum memory allocation is only 168 GB because "We use 6GB per core as a round number memory resource.  Multiplied by the core count of 28 gives 168GB.  The difference will be used by the operating system for file handling to make your jobs more efficient." ([reference](https://public.confluence.arizona.edu/display/UAHPC/Running+Jobs))) ([archived 4.22.2020](https://web.archive.org/web/20200423044116/https://public.confluence.arizona.edu/display/UAHPC/Running+Jobs)).
Thus these test cases are designed to fill as much of the 168GB of memory as possible.

The amount of memory is measured with `/usr/bin/time -v` in the run script, from the entry "Maximum resident set size (kbytes)".
This method is limited in two ways:
1. It can only measure memory usage at the resolution of a whole virtual memory page (4096 bytes on Ocelote, as with most Linux systems).
2. It can only measure memory usage of a single executable, making true memory measurements of multi-process programs (i.e. MPI programs) impossible.

We deal with this in two ways:
1. We are not interested in sub-megabyte memory measurement resolution.
2. We only perform memory measurements on single-process executions of ParFlow.

Currently (4.23.2020) there are discussions about the accuracy of measuring memory [[#2]](https://github.com/CompOpt4Apps/IanHydroframeWork/issues/2) and alternative methods that include the ability to measure the memory of multi-process ParFlow executions [[#7]](https://github.com/CompOpt4Apps/IanHydroframeWork/issues/7).

# Running PBS Test Case Scripts

***PLEASE READ THESE INSTRUCTIONS COMPLETELY AND CAREFULLY!***

This process is simple, but you need to follow the instructions.
Not following the instructions will result in time wasted in queues and unnecessary confusion.
This document assumes some minimal experience with PBS and Bash.

Your tasks are primarily setting the proper variables in the script.
This should be done by editing the script (or a copy of the script) where indicated.
After this is completed, you can run the script with PBS.

## Setting Up Environment
There are two environmental components that need to be setup in the test script.
1. The path to the sinusoidal scripts directory.
2. The ParFlow installation environment

### Setting the Path to Script Directory
Most importantly `path_to_script_directory` must be set with the absolute path to the `test_domains/sinusoidal/scripts` directory.
The path should not end with a `/` (e.x. `/thiecho "This is output to the terminal"s/is/an/ok/path`, `/this/is/NOT/an/ok/path/`).

Using a text editor or `sed`, replace the string `"PUT THE PROPER SCRIPTS DIRECTORY PATH HERE"` with the correct value and save the script.

### Setting the ParFlow Installation Environment

Second, you must choose how the script knows about the ParFlow installation you would like it to use.
This can be done in one of two ways:
+ Setting the PARFLOW_DIR variable.
  * Used for local installations.
+ Setting the modules_array variable.
  * Used if desired ParFlow installation is contained in a module.

#### PARFLOW_DIR
If the desired ParFlow installation is local (e.g. somewhere in or under your home directory), you should set the `PARFLOW_DIR` path.
`PARFLOW_DIR` is an existing environment variable required for ParFLow installations.
`PARFLOW_DIR` should already point to a ParFLow installation directory that contains the bin, lib, and include directories.

If you know you have a local ParFlow installation, but don't know the value of `PARFLOW_DIR`, run the `echo ${PARFLOW_DIR}`

Using a text editor or `sed`, replace the string `"PUT THE PROPER PARFLOW_DIR PATH HERE"` with the correct value and save the script.

#### ParFlow Modules
If the desired ParFlow installation is installed in a global module (such as the `parflow/3/3.6.0` module on Ocelote), you should set the `modules_array` array.
`modules_array` is an array of module names that will be loaded in the order they are specified in the array.

Using a text editor, add the list of modules names in between the parenthesis of the definition for `module_array`.

As an example, to use the ParFlow installed with the `mstrout/parflow/parflow-master-9c0b0f_amps-mpi` module:
```bash
modules_array=(unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi)
```
This is (as of 4.22.202) valid on Ocelote.

## Setting Sepecific PBS settings
Each test case has default PBS settings that you may need to change.

### group_list
Chief among them is the `group_list` parameter.
Currently the default is `mstrout` for Dr. Strout's Ocelote group.
If you are not in that group, you should change that parameter to the group you are in.

This is simply done by replacing `mstrout` by the group name you are a part of.

### Different PBS Systems
As a word of caution, I (Ian Bertolacci) have occasionally noticed in PBS documents and tutorials that PBS usage appears to be different in some cases.
This could be due to PBS version differences, or system specific settings, or the alignment of the moon's phase with anti-axis of the writers authors astrological sign.
So be aware that your PBS system may not agree with the PBS flags and configuration methods used in the PBS scripts provided here.

## Running Test Case
Having modified the test cases, we can now run it with the PBS job scheduler.
None of the provided test cases require additional arguments.

It is recommended to do this in a directory created specifically to collect the output data.

For example, running a setup Large Squarish domain.
```bash
# In test_domains/sinusoidal
cd path/to/test_domains/sinusoidal

# make a testing directory
mkdir test_large_squarish
cd test_large_squarish

# Execute large squarish
qsub ../test_cases/large_squarish.pbs
################################################################################
# BEGIN output from `qsub ../test_cases/large_squarish.pbs`
################################################################################
# 1234567.head1.cm.cluster
################################################################################
# END output from `qsub ../test_cases/large_squarish.pbs`
################################################################################

# Output from the test is stored in an output file named by the
# PBS script name (-N) parameter and the job ID printed by the qsub command.
cat large_squarish_ocelote_big_sinusoidal.o1234567
################################################################################
# BEGIN output from `cat large_squarish_ocelote_big_sinusoidal.o1234567`
################################################################################
# Currently Loaded Modulefiles:
#  1) pbspro/19.2.4                                   
#  2) gcc/6.1.0(default)                              
#  3) unsupported/1.0                                 
#  4) gcc/7.2.0                                       
#  5) openmpi/gcc/1.10.2(default)                     
#  6) python/2/2.7.14                                 
#  7) hdf5_18/1.8.20                                  
#  8) silo/4/4.10.2                                   
#  9) hypre/2/2.9.0b                                  
# 10) hdf5/1.8.18                                     
# 11) mstrout/parflow/parflow-master-9c0b0f_amps-mpi  
# /unsupported/mstrout/parflow/parflow-master-9c0b0f_amps-mpi/bin/parflow
# Running: 5000x5223x5-2_1-1-1
# ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/run.sh 1 1 1 5000 5223 5 2 ocelote_large_squarish_5000x5223x5-2_1-1-1
# Run Name: ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43
# Test Root Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/..
# Output Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs
# Test Scripts Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../scripts
# Test Files Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../assets
# Run Output Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs/ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43
# ${HOME}/IanHydroframeWork/test_domains/sinusoidal/outputs/ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43
# Running: /usr/bin/time -v tclsh sinusoidal.tcl 1 1 1 5000 5223 5 2 ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43
#
# 	Command being timed: "tclsh sinusoidal.tcl 1 1 1 5000 5223 5 2 ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43"
# 	User time (seconds): 1811.67
# 	System time (seconds): 166.89
# 	Percent of CPU this job got: 99%
# 	Elapsed (wall clock) time (h:mm:ss or m:ss): 33:01.81
# 	Average shared text size (kbytes): 0
# 	Average unshared data size (kbytes): 0
# 	Average stack size (kbytes): 0
# 	Average total size (kbytes): 0
# 	Maximum resident set size (kbytes): 175495240
# 	Average resident set size (kbytes): 0
# 	Major (requiring I/O) page faults: 152
# 	Minor (reclaiming a frame) page faults: 73049099
# 	Voluntary context switches: 1716
# 	Involuntary context switches: 203291
# 	Swaps: 0
# 	File system inputs: 81632
# 	File system outputs: 208
# 	Socket messages sent: 0
# 	Socket messages received: 0
# 	Signals delivered: 0
# 	Page size (bytes): 4096
# 	Exit status: 0
# ===================================================
# Output Log File
# Node 0: Using process grid (1,1,1)
# Node 0: Well Information
# Node 0: No Wells.
# Node 0: Well Information
# Node 0: No Wells.
# Node 0: Problem solved
# ===================================================
# Timing Log File
# Timer,Time (s),MFLOPS (mops/s),FLOP (op)
# Solver Setup,76.603600,0.000000,0
# Solver,1874.891600,0.557152,1.0446e+09
# Solver Cleanup,14.882000,0.000000,0
# Matvec,0.000000,-nan,0
# PFSB I/O,0.000000,-nan,0
# PFB I/O,0.000000,-nan,0
# CLM,0.000000,-nan,0
# PFSOL Read,0.000000,-nan,0
# Clustering,765.955500,0.000000,0
# Permeability Face,0.000000,-nan,0
# Godunov Advection,0.000000,-nan,0
# Geometries,748.246200,0.000000,0
# SubsrfSim,4.437700,0.000000,0
# Porosity,0.300100,0.000000,0
# PhaseRelPerm,75.565400,0.000000,2
# PFMG,0.000000,-nan,0
# HYPRE_Copies,0.000000,-nan,0
# NL_F_Eval,229.889600,0.000000,2
# KINSol,232.283800,4.497085,1.0446e+09
# Total Runtime,1978.452600,-nan,0
# ===================================================
# Your group mstrout has been charged 15:25:24 (0:33:03 X 28 cpus).
# You previously had 18284:28:26.  You now have 18269:03:02 of standard_time remaining
################################################################################
# END output from `cat large_squarish_ocelote_big_sinusoidal.o1234567`
################################################################################

# The directory the test was run in, and where all of the output resides
# is displayed in the output, shown by "Run Output Path: path/to/test_domains/sinusoidal/scripts/../outputs/<run name>_<timestamp>"
# In this case the output directory is ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs/ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43

# Going into output directory
cd ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs/ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43

# Show output files
ls
################################################################################
# BEGIN output from `ls`
################################################################################
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.out.kinsol.log
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.out.log
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.out.pfmetadata
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.out.pftcl
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.out.timing.csv
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.out.txt
ocelote_large_squarish_5000x5223x5-2_1-1-1_proc-1-1-1_size-5000x5223x5_time-2_04-22_14:30:43.pfidb
sinusoidal.tcl
################################################################################
# END output from `ls`
################################################################################
```

The section "100% Complete, Clone to Run Example" has a full example of running the "Hello World PBS" test case, which is identical to running Large Squarish (but takes 5 minutes instead of 30).

# 100% Complete, Clone to Run examples
Here are some examples of starting from nothing, and running test cases.

Some of these examples demonstrate the process of executing PBS test cases, including editing copies of the test case script and spawning a PBS job.

# Hello World Manually
This shows an example of running the sinusoidal domain manually, using the same parameters from the Hello World Script test case.

This example clones this repository to the home directory, creates a new test directory for managing test scripts and output, sets up the domain configuration in the local Bash environment, and executes the run script.


# Hello World PBS Test Case
This shows an example of running the Hello World PBS test case starting from scratch.
Hello World PBS test case is shown here because it's usage is identical to the other PBS based test cases (unless otherwise noted).

This example clones this repository to the home directory, creates a new test directory for managing test scripts and output, makes and edits a copy of `tests/hello_world.pbs`, and spawns a PBS job for the edited script.
In this case, we are using the `modules_array` method of specifying the ParFlow environment, and will use the `mstrout/parflow/parflow-master-9c0b0f_amps-mpi` module installed on Ocelote (which is part of the `unsupported` family of Ocelote modules).

This case makes edits using `sed`, specifically because I don't know how to show making edits with `vim` in a code block example.
Regardless, the resulting script is displayed in full, with commends denoting where edits were made.

```bash
# Start in home directory
cd ${HOME}

# Clone this repository
git clone git@github.com:CompOpt4Apps/IanHydroframeWork.git
################################################################################
# BEGIN output from `git clone git@github.com:CompOpt4Apps/IanHydroframeWork.git`
################################################################################
# Cloning into 'IanHydroframeWork'...
# remote: Enumerating objects: 104, done.
# remote: Counting objects: 100% (104/104), done.
# remote: Compressing objects: 100% (59/59), done.
# remote: Total 104 (delta 32), reused 89 (delta 24), pack-reused 0
# Receiving objects: 100% (104/104), 40.51 KiB | 482.00 KiB/s, done.
# Resolving deltas: 100% (32/32), done.
################################################################################
# BEGIN output from `git clone git@github.com:CompOpt4Apps/IanHydroframeWork.git`
################################################################################

# Go into the sinusoidal test domain directory
cd ${HOME}/IanHydroframeWork/test_domains/sinusoidal

# Making a separate directory for this test.
# This is where I will copy, edit, keep, and run
# my copy of the hello_world.pbs script
mkdir test_4.22.2020_full_run_hello_world_pbs

# Copying the hello_world.pbs into my new test directory
cp ./test_cases/hello_world.pbs test_4.22.2020_full_run_hello_world_pbs/my_hello_world.pbs

# Going into my test directory
cd test_4.22.2020_full_run_hello_world_pbs

# Setting the path_to_script_directory to ${HOME}/IanHydroframeWork/test_domains/sinusoidal
# I am using  sed, but the same can be accomplished with favorite text editor
# and doing the same edit manually.
sed "s|path_to_script_directory=\"PUT THE PROPER SCRIPTS DIRECTORY PATH HERE\"|path_to_script_directory=${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts # Changed path_to_script_directory here|g" --in-place ./my_hello_world.pbs

# Setting modules_array to (unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi)
# I'm changing modules_array because I want to use
# the module mstrout/parflow/parflow-master-9c0b0f_amps-mpi
# I am using  sed, but the same can be accomplished with favorite text editor
# and doing the same edit manually.
sed "s|modules_array=([[:space:]]*)|modules_array=(unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi) # Changed modules_array here|g" --in-place ./my_hello_world.pbs

# Because I am using modules_array to set my ParFlow installation,
# I am NOT setting the PARFLOW_DIR variable.
# However, if I wanted to use one of my local installations,
# such as the one in ${HOME}/hydroframe/parflow/master/install,
# I would do something like this. I am using  sed, but the same can be
# accomplished with favorite text editor and doing the same edit manually.
# sed "s|PARFLOW_DIR=\"PUT THE PROPER PARFLOW_DIR PATH HERE\"|PARFLOW_DIR=${HOME}/hydroframe/parflow/master/install # Changed PARFLOW_DIR here|g" --in-place ./my_hello_world.pbs

# Showing the resulting script for completeness
cat my_hello_world.pbs
################################################################################
# BEGIN output from `cat my_hello_world.pbs`
################################################################################
# #!/usr/bin/env bash
# # Job will use 1 node, 28 cores, and 168gb of memory total.
# #PBS -l select=1:ncpus=28:mem=168gb:pcmem=6gb
# #PBS -q standard
# #PBS -N hello_world_pbs
# #PBS -W group_list=mstrout
# #PBS -l place=pack:shared
# #PBS -l walltime=00:05:00
# #PBS -j oe
#
# #set number of cells
# NX=100
# NY=200
# NZ=10
#
# # Run for 24 hours
# NT=24
#
# # 8 processes, making 4 partitions in the X dimension, and 2 in the Y.
# NP=4
# NQ=2
# NR=1
#
# size_string=${NX}x${NY}x${NZ}-${NT}_${NP}-${NQ}-${NR}
# test_name=hellow_world_pbs_${size_string}
#
# #▉    ▉  ▉▉▉▉▉▉   ▉   ▉           ▉   ▉   ▉▉▉▉   ▉    ▉      ▉▉▉▉▉▉▉
# #▉    ▉  ▉         ▉ ▉             ▉ ▉   ▉    ▉  ▉    ▉       ▉▉▉▉▉
# #▉▉▉▉▉▉  ▉▉▉▉▉      ▉               ▉    ▉    ▉  ▉    ▉        ▉▉▉
# #▉    ▉  ▉          ▉               ▉    ▉    ▉  ▉    ▉         ▉
# #▉    ▉  ▉          ▉   ▉▉▉         ▉    ▉    ▉  ▉    ▉
# #▉    ▉  ▉▉▉▉▉▉     ▉   ▉▉▉         ▉     ▉▉▉▉    ▉▉▉▉          ▉
# #                        ▉
# #                       ▉
# #
# # You need change the below variables
#
# # Setting the Path to Script Directory
# #
# # path_to_script_directory is the absolute path to
# # the script directory containing run.sh
# # THIS IS MANDATORY
# # Change the below string to the correct path.
# #                    └──────────────────────┐
# #                        ┌──────────────────┴────────────────────────┐
# path_to_script_directory=${HOME}/IanHydroframeWork_modules/test_domains/sinusoidal/scripts # Changed path_to_script_directory here
#
#
# # Setting ParFlow installation
# #
# # ParFlow installation can be set in either one of two ways.
# # First: PARFLOW_DIR
# # PARFLOW_DIR points to the installation of ParFlow, and contains the
# # bin, lib, and include directories.
# # Change the below string to the correct path.
# #                    └─────────┐
# #           ┌──────────────────┴──────────────────┐
# PARFLOW_DIR="PUT THE PROPER PARFLOW_DIR PATH HERE"
#
# # Second: module_array
# # module_array lists the modules to be loaded in order.
# # Spefify the modules that need to be loaded, in the order in which they need to be loaded,
# # separated by SPACES into the empty array below, between the parenthesis
# #                ┌────────────────────┘
# #             ┌──▼──┐
# modules_array=(unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi) # Changed modules_array here
# # Valid (as of 4.22.202) example on Ocelote:
# # modules_array=(unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi)
#
# # And you're done!
# # You can set the debug variable to true and run with or without PBS to
# # test these setupt without actually running ParFlow
# enable_debug=false
#
# ################################################################################
# # Nothing below here should be changed unless you know what you're doing.
# ################################################################################
#
# # Check path_to_script_directory
# if [[ ${path_to_script_directory} == "PUT THE PROPER SCRIPTS DIRECTORY PATH HERE" ]]
# then
#   # Script being executed by PBS, no recourse for finding path_to_script_directory
#   if [[ "$0" =~ "/pbs" ]]
#   then
#     echo "path_to_script_directory HAS NOT BEEN SET PROPERLY."
#     echo "path_to_script_directory=${path_to_script_directory}"
#     echo "YOU DID NOT FOLLOW THE README OR THE INSTRUCTIONS LISTED HERE."
#     echo "SCRIPT IS BEING RUN WITH PBS, AND CANNOT AUTOMAGICALLY DETECT"
#     echo "THE PATH TO THE RUN SCRIPT FOR YOU."
#     exit
#
#   # Script probably not being executed by PBS.
#   # Warn user, but attempt to find path_to_script_directory
#   else
#     echo "path_to_run_script has not been set properly."
#     echo "Currently: path_to_script_directory=${path_to_script_directory}"
#     echo "Please read the instructions available both here and in the readme."
#     echo "This script will attempt to determine the path to the runscript"
#
#     # Derive possible path from script invocation path
#     path_to_script_directory=$(readlink -f $0 | sed "s|test_cases/$(basename $0)|scripts|g")
#     # Check possible path
#     if [[ ! -d ${path_to_script_directory} ]]
#     then
#       echo "Could not find path to the scripts directory."
#       echo "Please read the instructions available both here and in the readme,"
#       echo "and set path_to_run_script properly."
#       exit
#     fi
#
#     echo "Attempting to use ${path_to_script_directory} as path_to_script_directory."
#   fi
# fi
#
# if [[ ! -e ${path_to_script_directory}/run.sh ]]
# then
#   echo "Cannot find run.sh in ${path_to_script_directory}"
#   echo "Is the path correct?"
#   exit
# fi
#
# # Check PARFLOW_DIR
# if [[ ${PARFLOW_DIR} != "PUT THE PROPER PARFLOW_DIR PATH HERE" ]] && [[ ${PARFLOW_DIR} != "" ]]
# then
#   # Check PARFLOW_DIR is a directory
#   if [[ ! -d ${PARFLOW_DIR} ]]
#   then
#     echo "PARFLOW_DIR provided but either does not exist or is not a directory: ${PARFLOW_DIR}"
#     exit
#   fi
#   # Upate path with this PARFLOW_DIR's bin, export both.
#   PATH=${PARFLOW_DIR}/bin:${PATH}
#   export PATH PARFLOW_DIR
#
# # Check modules array
# elif [[ ${#modules_array[@]} > 0 ]]
# then
#   # Load each module in order, checking exit status
#   for load_module in ${modules_array[@]}
#   do
#     module load ${load_module}
#     load_exit_code=$?
#     # Check successful load
#     if [[ ${load_exit_code} != 0 ]]
#     then
#       echo "Error loading module: ${load_module}"
#       echo "Exit code ${load_exit_code}"
#       exit
#     fi
#   done
#
# # Neither method used. Warn, exit.
# else
#   echo "No method of setting up ParFlow environment was chosen."
#   echo "Please read instructions and try again."
#   exit
# fi
#
# # Sanity check environment
# module list
# which parflow
#
# # Check for parflow on path
# if [[ $(which parflow) == "" ]]
# then
#   echo "No parflow binary found on path."
#   exit -1
# fi
#
# # Execute run script
# cmd="${path_to_script_directory}/run.sh ${NP} ${NQ} ${NR} ${NX} ${NY} ${NZ} ${NT} ${test_name}"
# echo "Running: ${size_string}"
# echo ${cmd}
# if [[ "${enable_debug}" != "true" ]]
# then
#   eval ${cmd}
# fi
################################################################################
# END output from `cat my_hello_world.pbs`
################################################################################

qsub ./my_hello_world.pbs
################################################################################
# BEGIN output from `qsub ./my_hello_world.pbs`
################################################################################
# 3161983.head1.cm.cluster
################################################################################
# END output from `qsub ./my_hello_world.pbs`
################################################################################

# Now we have to wait for this job to complete.
# Should be quick, but getting through the queue can take some time.

# Once the job is complete, we can view its output.
cat hello_world_pbs.o3161983
################################################################################
# BEGIN output from `cat hello_world_pbs.o3161983`
################################################################################
# Currently Loaded Modulefiles:
#  1) pbspro/19.2.4                                   
#  2) gcc/6.1.0(default)                              
#  3) unsupported/1.0                                 
#  4) gcc/7.2.0                                       
#  5) openmpi/gcc/1.10.2(default)                     
#  6) python/2/2.7.14                                 
#  7) hdf5_18/1.8.20                                  
#  8) silo/4/4.10.2                                   
#  9) hypre/2/2.9.0b                                  
# 10) hdf5/1.8.18                                     
# 11) mstrout/parflow/parflow-master-9c0b0f_amps-mpi  
# /unsupported/mstrout/parflow/parflow-master-9c0b0f_amps-mpi/bin/parflow
# Running: 100x200x10-24_4-2-1
# ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/run.sh 4 2 1 100 200 10 24 hello_world_pbs_100x200x10-24_4-2-1
# Run Name: hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43
# Test Root Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/..
# Output Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs
# Test Scripts Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../scripts
# Test Files Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../assets
# Run Output Path: ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs/hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43
# ${HOME}/IanHydroframeWork/test_domains/sinusoidal/outputs/hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43
# Running: /usr/bin/time -v tclsh sinusoidal.tcl 4 2 1 100 200 10 24 hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43
#
# 	Command being timed: "tclsh sinusoidal.tcl 4 2 1 100 200 10 24 hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43"
# 	User time (seconds): 10.27
# 	System time (seconds): 0.90
# 	Percent of CPU this job got: 426%
# 	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:02.62
# 	Average shared text size (kbytes): 0
# 	Average unshared data size (kbytes): 0
# 	Average stack size (kbytes): 0
# 	Average total size (kbytes): 0
# 	Maximum resident set size (kbytes): 48344
# 	Average resident set size (kbytes): 0
# 	Major (requiring I/O) page faults: 348
# 	Minor (reclaiming a frame) page faults: 186882
# 	Voluntary context switches: 6171
# 	Involuntary context switches: 417
# 	Swaps: 0
# 	File system inputs: 49224
# 	File system outputs: 7824
# 	Socket messages sent: 0
# 	Socket messages received: 0
# 	Signals delivered: 0
# 	Page size (bytes): 4096
# 	Exit status: 0
# ===================================================
# Output Log File
# Node 0: Using process grid (4,2,1)
# Node 0: Well Information
# Node 0: No Wells.
# Node 0: Well Information
# Node 0: No Wells.
# Node 0: Problem solved
# ===================================================
# Timing Log File
# Timer,Time (s),MFLOPS (mops/s),FLOP (op)
# Solver Setup,0.155900,0.000000,0
# Solver,1.140700,16.831791,1.92e+07
# Solver Cleanup,0.007000,0.000000,0
# Matvec,0.000000,-nan,0
# PFSB I/O,0.000000,-nan,0
# PFB I/O,0.000000,-nan,0
# CLM,0.006700,0.000000,0
# PFSOL Read,0.000000,-nan,0
# Clustering,0.342900,0.000000,0
# Permeability Face,0.000000,-nan,0
# Godunov Advection,0.000000,-nan,0
# Geometries,0.256800,0.000000,0
# SubsrfSim,0.002100,0.000000,0
# Porosity,0.000100,0.000000,0
# PhaseRelPerm,0.190900,0.000126,24
# PFMG,0.000000,-nan,0
# HYPRE_Copies,0.000000,-nan,0
# NL_F_Eval,0.587100,0.000041,24
# KINSol,0.598800,32.064168,1.92e+07
# Total Runtime,1.315500,-nan,0
# ===================================================
################################################################################
# END output from `cat hello_world_pbs.o3161983`
################################################################################

# The directory the test was run in, and where all of the output resides
# is displayed in the output, shown by "Run Output Path: path/to/test_domains/sinusoidal/scripts/../outputs/<run name>_<timestamp>"
# In this case the output directory is ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs/hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_13:24:47

# Going into output directory
cd ${HOME}/IanHydroframeWork/test_domains/sinusoidal/scripts/../outputs/hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43

# Show output files
ls
################################################################################
# BEGIN output from `ls`
################################################################################
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.out.kinsol.log
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.out.log
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.out.pfmetadata
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.out.pftcl
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.out.timing.csv
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.out.txt
hello_world_pbs_100x200x10-24_4-2-1_proc-4-2-1_size-100x200x10_time-24_04-22_14:30:43.pfidb
sinusoidal.tcl
################################################################################
# END output from `ls`
################################################################################
```
