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

# Example Usage

Here is a demonstration of using the sinusoidal test domain
```bash
> cat ./test_cases/hello_world.sh
#!/usr/bin/env bash
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

# Create path to actual run script
# Change if moving script somewhere other than test_domains/sinusoidal/examples
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

> ./test_cases/hello_world.sh
Run Name: hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
Test Root Path: path/to/repo/test_domains/sinusoidal/scripts/..
Output Path: path/to/repo/test_domains/sinusoidal/scripts/../outputs
Test Scripts Path: path/to/repo/test_domains/sinusoidal/scripts/../scripts
Test Files Path: path/to/repo/test_domains/sinusoidal/scripts/../assets
Run Output Path: path/to/repo/test_domains/sinusoidal/scripts/../outputs/hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
path/to/repo/test_domains/sinusoidal/outputs/hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34
Running: /usr/bin/time -v tclsh sinusoidal.tcl 4 2 1 100 200 10 24 hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34

	Command being timed: "tclsh sinusoidal.tcl 4 2 1 100 200 10 24 hello_world_proc-4-2-1_size-100x200x10_time-24_04-22_14:31:34"
	User time (seconds): 21.56
	System time (seconds): 2.55
	Percent of CPU this job got: 345%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:06.98
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 57016
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 29
	Minor (reclaiming a frame) page faults: 87045
	Voluntary context switches: 7551
	Involuntary context switches: 1364049
	Swaps: 0
	File system inputs: 0
	File system outputs: 46664
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0
===================================================
Output Log File
Node 0: Using process grid (4,2,1)
Node 0: Well Information
Node 0: No Wells.
Node 0: Well Information
Node 0: No Wells.
Node 0: Problem solved
===================================================
Timing Log File
Timer,Time (s),MFLOPS (mops/s),FLOP (op)
Solver Setup,0.455600,0.000000,0
Solver,5.829700,3.293484,1.92e+07
Solver Cleanup,0.020300,0.000000,0
Matvec,0.000000,0.000000,0
PFSB I/O,0.000000,0.000000,0
PFB I/O,0.000000,0.000000,0
CLM,0.226000,0.000000,0
PFSOL Read,0.000000,0.000000,0
Clustering,1.923100,0.000000,0
Permeability Face,0.000000,0.000000,0
Godunov Advection,0.000000,0.000000,0
Geometries,1.114100,0.000000,0
SubsrfSim,0.074000,0.000000,0
Porosity,0.001100,0.000000,0
PhaseRelPerm,0.696100,0.000034,24
PFMG,0.000000,0.000000,0
HYPRE_Copies,0.000000,0.000000,0
NL_F_Eval,2.486300,0.000010,24
KINSol,3.032900,6.330583,1.92e+07
Total Runtime,6.298500,-nan,0
===================================================
```

There are more examples of using the sinusoidal test domain in `./test_cases`, including the "big" Ocelote tests.
For the "big" Ocelote tests, please see Ocelote_Readme.md

# Script Arguments
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
  - This becomes part of a path so do not used spaces or special characters other than: - _ .

^For the process topology, the total number of processes executing is the
product of the processes in each dimension (i.e. for *any* topolgy using any permutation of 2, 3, and 4, the total number of processes is 24 (2 x 3 x 4))

# Internal Script Configurations
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


# Other Details and Notes:

## Dump interval
The tcl script is configured to only dump at the end of the run.
