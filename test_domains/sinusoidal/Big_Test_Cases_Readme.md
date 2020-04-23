# Big Test Cases
This Readme documents the implementation and use of the "big" test cases.

All the test cases can be used either as a PBS test scripts (which can be used as a Bash script if need be).
All the test cases are have the following PBS configuration:
```bash
# 1 node, 28 cores, 168GB memory total, 6GB memory per core
#PBS -l select=1:ncpus=28:mem=168gb:pcmem=6gb
# Standard queue
#PBS -q standard
# Use mstrout time (You will need to change this if you are not in Dr. Strout's Ocelote group)
#PBS -W group_list=mstrout
# Give job exclusive access to node.
#PBS -l place=pack:exclhost
# Execute for 1 wall-clock hours, 140 (28*5) core hours
#PBS -l walltime=1:00:00
# Output stdout and stderr to same file
#PBS -j oe
```

You will need to change the `group_list` parameter if you are not in Dr. Strout's Ocelote group.

# Test Cases

## Large Squarish

* File: `test_cases/large_squarish.sh`
* Parameters:
  + NP: 1
  + NQ: 1
  + NR: 1
  + NX:
  + NY:
  + NZ: 5
  + NT: 2
* Observed Memory Occupation:
* Observed Runtime:

This test case has NX and NY parameters that are roughly equal (1-(min(nx,ny)/max(nx,ny)% off square).


# How To Run

**PLEASE READ THESE INSTRUCTIONS COMPLETELY AND CAREFULLY!**

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
The path should not end with a `/` (e.x. `/this/is/an/ok/path`, `/this/is/NOT/an/ok/path/`).

Using a text editor or `sed`, replace the string `"PUT THE PROPER SCRIPTS DIRECTORY PATH HERE!"` with the correct value and save the script.

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

Using a text editor or `sed`, replace the string `"PUT THE PROPER PARFLOW_DIR PATH HERE!"` with the correct value and save the script.

#### ParFlow Modules
If the desired ParFlow installation is installed in a global module (such as the `parflow/3/3.6.0` module on Ocelote), you should set the `modules_array` array.
`modules_array` is an array of module names that will be loaded in the order they are specified in the array.

Using a text editor, add the list of modules names in between the parenthesis of the definition for `module_array`.

As an example, to use the ParFlow installed with the `mstrout/parflow/parflow-master-9c0b0f_amps-mpi` module:
```bash
modules_array=(unsupported mstrout/parflow/parflow-master-9c0b0f_amps-mpi)
```
This is (as of 4.22.202) valid on Ocelote.

## Running Test Case
Having modified the test cases, we can now run it with the PBS job scheduler.
None of the provided test cases require additional arguments.

It is recommended to do this in a directory created specifically to collect the output data.

For example, running a setup Large Squarish domain.
```bash
# PWD is test_domains/sinusoidal
mkdir test_4.22.2020
cd test_4.22.2020
# Execute large squarish
qsub ../test_cases/large_squarish.pbs
<<OUTPUT
1234567.head1.cm.cluster
OUTPUT
# Output from the test is stored in an output file named by the
# PBS script name (-N) parameter and the job ID printed by the qsub command.
cat large_squarish_ocelote_big_sinusoidal.o1234567
<<OUTPUT
TODO OUTPUT
OUTPUT
```

The section "100% Complete, Clone to Run Example" has a full example of running the Large Q

# 100% Complete, Clone to Run Example
Below is a full example of running the Large Squarish test case, starting from nothing, cloning the repository, editing the script, starting the PBS job, and viewing the results.

```bash
TODO
```

# Background
These test cases have parameters chosen such that a test fills the memory of a standard, non-GPU node.
The configuration of Ocelote nodes can be found [here](https://public.confluence.arizona.edu/display/UAHPC/Compute+Resources) ([Archived version, dated 4.22.2020](https://web.archive.org/web/20200423043707/https://public.confluence.arizona.edu/display/UAHPC/Compute+Resources))
While Ocelote nodes have 192 GB of RAM, the recomended maximum memory allocation is only 168 GB because "We use 6GB per core as a round number memory resource.  Multiplied by the core count of 28 gives 168GB.  The difference will be used by the operating system for file handling to make your jobs more efficient." ([reference](https://public.confluence.arizona.edu/display/UAHPC/Running+Jobs)) ([archived 4.22.2020](https://web.archive.org/web/20200423044116/https://public.confluence.arizona.edu/display/UAHPC/Running+Jobs)).
Thus these test cases are designed to fill as much of the 168GB of memory as possible.

The amount of memory is measured with `/usr/bin/time -v` in the run script, from the entry "Maximum resident set size (kbytes)".
This method is limited in two ways:
1. It can only measure memory usage at the resolution of a whole virtual memory page (4096KB on Ocelote, as with most Linux systems).
2. It can only measure memory usage of a single executable, making true memory measurements of multi-process programs (i.e. MPI programs) impossible.

We deal with this in two ways:
1. We are not interested in sub-megabyte memory measurement resolution.
2. We only perform memory measurements on single-process executions of ParFlow.
