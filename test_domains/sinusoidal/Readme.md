# Sinusoidal Test Case
Sinusoidal is a ParFlow test case for exploring performance across parameterized domain
sizes.  The tcl script for this test case is parameterized by the name of the test,
the number of X, Y, and Z cells, the number of simulated time steps in hours, and the 
number of processors that should evenly partition the work in each of the X, Y, and Z directions.
This test case was adapted from the pfp4 test case from Stefan Kollet, and
was described as a weak scaling with periodic boundary conditions.

Since using the tcl script involves setting all of the parameters as environment variables,
there is a `sinusoidal-run.sh` script that takes each of the parameters as command-line
parameters, sets up the environment variables, and runs the tcl script, which performs the
actual ParFlow execution.

FIXME: Ian, please rename the run script to sinuisoidal-run.sh.

FIXME: please put a couple of sentences here about the big test case and how to run it so that
it is in the first screenful people see.

For comprehensive documentation, see Manual.md and Ocelote_Readme.md (if using Ocelote or similar HPC system).

# Example Usage with just the tcl script
Below is an example of executing the tcl script in Bash.
```bash
# Make directory for collecting test outputs.
# This is one of the things managed by the run script (see Manual.md)
mkdir manual_sinusoidal
cd manual_sinusoidal

# Name of our test; names prefixes all the paths of the output files.
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

# There is no output from the tcl script.
# Printing the results when the script has is also handled by the run script (see Manual.md)
# There is also no timing command output, though aspects of the
# *timing.csv and *.out.log could make up for that, but are also present
# anyway when using the run script.

# But there are quite a few output
ls
########################
# BEGIN output from `ls`
########################
# hello_world.out.kinsol.log
# hello_world.out.log
# hello_world.out.pfmetadata
# hello_world.out.pftcl
# hello_world.out.timing.csv
# hello_world.out.txt
# hello_world.pfidb
######################
# END output from `ls`
######################

```

# TCL Script `sinusoidal-run.sh`
The tcl script `assets/sinusoidal.tcl` is what sets up the ParFlow database and executes ParFlow.
It can be used directly, but in larger processes (such performance data-collection) requires manual management 
of the output.

FIXME: why is sinuisoidal.tcl in a subdirectory?  Why not just in sinusoidal?

FIXME: show how to use sinusoidal-run.sh instead of having to do the above setup for tcl

## Script Arguments
Both the bash run-script and the tcl test scrip accepts the following parameters in this order:
+ Processes in X (NP)
  - Number of processes executing^ in X dimension.
+ Processes in Y (NQ)
  - Number of processes executing^ in Y dimension.
+ Processes in Z (NR)
  - Number of processes executing^ in Z dimension.
+ Size in X (NX)
  - Number of cells in the X dimension.
+ Size in Y (NY)
  - Number of cells in the Y dimension.
+ Size in Z (NZ)
  - Number of cells in the Z dimension.
+ Time steps (NT)
  - Number of time steps to simulate.
+ Test Name (optional)
  - Name used to prefix folders and files produced by this test
  - Default: sinusoidal.cpu
  - This becomes part of a path so do not used spaces or special characters other than any of the following: : - _ .

^For the process topology, the total number of processes executing is the
product of the processes in each dimension (i.e. for *any* topolgy using any permutation of 2, 3, and 4, 
the total number of processes is 24 (2 x 3 x 4))

# Specific Parameter-Sets of Interest
There are several specific test cases using the sinusoidal domain.

## Large Squarish
This test cases is designed to have a peak memory footprint near 168GB.
This test case has NX and NY parameters that are roughly equal (4.27% off-square).
It was designed for running on the UArizona HPC system Ocelote.

* File: `test_cases/large_squarish.pbs`
* Sinusoidal Parameters:
  + Number Processes X: 1
  + Number Processes Y: 1
  + Number Processes Z: 1
  + Number Cells X: 5000
  + Number Cells Y: 5223
  + Number Cells Z: 5
  + Number Timesteps: 2
* Observed metrics:
  + Memory Occupation: (162.76 GiB) 170666612 KiB
  + Runtime:  0:33:22.57 (2002.57 seconds)

FIXME: for the rest of the file, whenever possible make the text fit in <80 columns.  It isn't always possible
when there are URLs, but should happen everywhere else.

### Background
This test case has parameters chosen such that a test fills the memory of a standard, non-GPU node.
The configuration of Ocelote nodes can be found [here](https://public.confluence.arizona.edu/display/UAHPC/Compute+Resources) 
([archived 4.22.2020](https://web.archive.org/web/20200423043707/https://public.confluence.arizona.edu/display/UAHPC/Compute+Resources)).
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
