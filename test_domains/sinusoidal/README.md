# Sinusoidal Test Case
Sinusoidal is a test case for exploring performance across arbitrary
domain sizes.
This test case was adapted from the pfp4 test case from Stefan Kollet, and
was described as a weak scaling with periodic boundary condition.

Usage:
```bash
test_name=example_test_run

number_cells_X=10
number_cells_Y=100
number_cells_Z=20

number_timesteps=100

number_processes_X=4
number_processes_Y=2
number_processes_Z=1

./scripts/run.sh ${number_processes_X} ${number_processes_Y} ${number_processes_z} ${number_cells_X} ${number_cells_Y} ${number_cells_z} ${number_timesteps} ${test_name}
```

By default, this test prints out the ParFlow standard output,
and timing information from `/usr/bin/time` and ParFlow's internal timing system
(if it has been built with timing configured to on, see section on building ParFlow).

Output files from the test run can be found in `last_output` or in `outputs`.
In `outputs/`, each test run has its own directory named as  `<test_name>_<time_stamp_of_test_invocation>`.
`last_output` points to the most recently created test directory.


## Script Arguments
The test accepts the following parameters:
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
product of the processes in each dimension.

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


## Other Details and Notes:

### Dump interval
The tcl script is configured to only dump at the end of the run.

###
