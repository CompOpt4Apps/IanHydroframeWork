# ParFlow Run-Time and Memory Footprint Estimator
This tool estimates the run-time and memory footprint of a ParFlow test script.
The output is a report (in JSON format) of the script's configuration used in the estimation, and the results of that estimation.

# Explanation of Usage
The tool is designed to accept your tcl script and arguments to that script in *exactly* the same way you would use it in an actual run.
Essentially, you should be able to swap the `tclsh` command with the tool command.

For example, if a script needs to be run as follows:
```bash
tclsh pantano_wash_summer_monsoon.tcl 1 5  100 3 6  10
```

then the tool estimator would be run as follows:
```bash
/path/to/parflow_size_time_predictor.py pantano_wash_summer_monsoon.tcl 1 5  100 3 6  10
```

The only change is `tclsh` has been replaced with `/path/to/parflow_size_time_predictor.py `

# Report Format
The tool outputs the report as a JSON object with the following scheme:
```python
[
  {
    "configuration": {
      "grid": {
        "NX": "int",
        "NY": "int",
        "NZ": "int"
      },
      "time": {
        "time_steps": "float"
      },
      "process_topology": {
        "NP": "int",
        "NQ": "int",
        "NR": "int"
      }
    },
    "estimation": {
      "footprint": {
        "value": "float",
        "unit": "string",
        "error_bound": "float"
      },
      "runtime": {
        "value": "float",
        "unit": "string",
        "error_bound": "float"
      }
    }
  }
]
```
Here, the values are strings that name the type of values actually emitted in
the report.

The `configuration` key reports the values of parameters extracted from the tcl
script and used by the prediction model.
It includes the grid size (`grid.NX`, `grid.NY`, and `grid.NZ`),
timesteps (`time.time_steps`),
and process topology
(`process_topology`, `process_topology.NY`, `process_topology.NZ` )

The `estimation` key reports the predicted maximum footprint (`footprint`),
and predicted total runtime (`runtime`).
The numerical value of the prediction is `value` and `unit` is a
string naming the units that value measures.

The default prediction module uses `"kilobytes"` for the footprint
prediction and `"seconds"` as the unit for the runtime prediction.

The `error_bound` is the maximum error that we expect to see,
with 95% confidence.
In other words, there is a 95% chance that the true value of the
performance parameter is in the range
`value` - `error_bound` ... `value` + `error_bound`

The report can also have multiple configurations and estimates,
because it is possible for a single tcl script to perform multiple runs during
its execution.

JSON is the chosen format, because it is a well standardized format that is easy
 to parse in many languages using numerous libraries and tools, including
 command line tools like [jq](https://stedolan.github.io/jq/).


## Runnable Examples
Here are some real examples that can be run as shown
(with the correct paths used).
All examples are written in Bash.

### Little Washita
Below is an example of predicting the washita test
(parflow/tests/washita/tcl_scripts/LW_Test.tcl)
```bash
cd /path/to/parflow/tests/washita/tcl_scripts
/path/to/parflow_size_time_predictor.py LW_Test.tcl
################################################################################
# BEGIN output from `/path/to/parflow_size_time_predictor.py LW_Test.tcl`
################################################################################
[
  {
    "configuration": {
      "grid": {
        "NX": 41,
        "NY": 41,
        "NZ": 50
      },
      "time": {
        "time_steps": 12.0
      },
      "process_topology": {
        "NP": 1,
        "NQ": 1,
        "NR": 1
      }
    },
    "estimation": {
      "footprint": {
        "value": 228380.9992,
        "unit": "kilobyte"
      },
      "runtime": {
        "value": 1.0086,
        "unit": "second"
      }
    }
  }
]
################################################################################
# END output from `/path/to/parflow_size_time_predictor.py LW_Test.tcl`
################################################################################
```

### Sinusoidal
Below is an example of predicting sinusoidal domain using the parameters from
the Large Squarish test-case.
```bash
# Parameters used in the sinusoidal test case
test_name=estimating_example_test_run

number_cells_X=5000
number_cells_Y=5223
number_cells_Z=5

number_timesteps=100

number_processes_X=4
number_processes_Y=2
number_processes_Z=1

# Report output file

# Running estimator tool
./parflow_size_time_predictor.py \
  ../../test_domains/sinusoidal/assets/sinusoidal.tcl \
  ${number_processes_X} ${number_processes_Y} ${number_processes_Z} \
  ${number_cells_X} ${number_cells_Y} ${number_cells_Z} \
  ${number_timesteps} \
  ${test_name}

################################################################################
# BEGIN output from `./parflow_size_time_predictor.py  ...`
################################################################################
[
  {
    "configuration": {
      "grid": {
        "NX": 5000,
        "NY": 5223,
        "NZ": 5
      },
      "time": {
        "time_steps": 100.0
      },
      "process_topology": {
        "NP": 4,
        "NQ": 2,
        "NR": 1
      }
    },
    "estimation": {
      "footprint": {
        "value": 175218048.99403062,
        "error_bound": 170786.46950405478,
        "unit": "kilobyte"
      },
      "runtime": {
        "value": 2311.579820088611,
        "error_bound": 47.95722951718799,
        "unit": "second"
      }
    }
  }
]
################################################################################
# END output from `./parflow_size_time_predictor.py  ...`
################################################################################
```

# Complete Usage

positional arguments:
  file_path             Path to the input tcl script.
  execution_arguments   Parameters necessary to execute the input tcl script,
                        if any.

optional arguments:
* -h, --help
  - Show this help message and exit

* --report-output REPORT_OUTPUT_PATH
  - Specify path to write report output to instead of standard out.

* --generated-script-path GENERATED_SCRIPT_PATH
  - Specify path of new script file generated by this tool.
  - Default: <file_path>.<GENERATED_SCRIPT_SUFFIX>

* --allow-clobber
  - Allows overwriting of existing files.

* --generated-script-suffix GENERATED_SCRIPT_SUFFIX
  - Specify suffix for creating the path of new script file generated by this
    tool.
  - Default: .size_determination.generated.tcl

* --backup-suffix BACKUP_SUFFIX
  - Suffix used when --in-place-generation set without exact path.
  - Default: .size_determination.automated_backup.original.tcl

* --in-place-generation [BACKUP_PATH]
  - Enables in-place generation of new script.
  - Instead of writing generated script to a new location, makes backup of
    input script and writes generated script to <file_path>.
  - Optional argument BACKUP_PATH specifies exact path to place backup of
    input script.
  - Default: <file_path>.<BACKUP_SUFFIX>

* --no-execute
  - Disables execution of generated script and prediction of runtime and
    footprint.

* --exact-command
  - Script parameters will instead be interpreted as a full execution command
    without any modifications or additions.

* --tcl-shell TCL_SHELL
  - Command used to execute tcl scripts.
  - Default: tclsh

* --prediction-module PREDICTION_MODULE
  - Set path to prediction module.
  - Default: ./default_prediction_module.py

* --footprint-prediction-function FOOTPRINT_PREDICTION_FUNCTION
  - Set function from prediction module to use to predict ParFlow footprint.
  - Default: "footprint_prediction_function"

* --runtime-prediction-function RUNTIME_PREDICTION_FUNCTION
  - Set function from prediction module to use to predict ParFlow runtime.
  - Default: "runtime_prediction_function"

* --debug:
  - Enable debugging output in tool.

# Requirements

## ParFlow
ParFlow should be installed and the environment set-up for running ParFlow for
this tool to operate correctly.
At a very minimum, the ParFlow tcl scripts should be installed somewhere.

## Python
This tool requires Python3.
It only uses modules in the standard library.

## TCL
This tool uses tcl.
A reasonably new version of tcl should be installed.
If necessary, the specific tcl shell command can be specified using the
`--tcl-shell TCL_SHELL` command line option.


# Prediction Module
The tool was developed in a way that allows users to easily write and change
prediction modules.
The default prediction module is `default_prediction_module.py`.
An alternative module can be used by invoking the
`--prediction-module PATH/TO/MODULE/FILE.py` command line option.

A prediction module is a separate python module which has at least two
functions:
```python
module_default_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z )
module_default_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z )
```
These are the default functions used by the tool.
Other functions can be defined.
Those functions can be used by invoking the
`--runtime-prediction-function FUNCTION_NAME`
and/or `--footprint-prediction-function FUNCTION_NAME` flags.

All prediction functions are required accept all the named parameters, but are
not required to use them.
All prediction functions are required to return a dictionary with the
following scheme:
```python
{
  "value": numerical,
  "unit": string,
  "error_bound": numerical
}
```

The tool will check that the returned prediction is a correctly formatted
dictionary as well as check that the value is a valid (> 0) real numerical
value.

Below is an extremely simple example prediction module implementation:
```python
#NOTE! This is merely a code example demonstrating prediction module implementation!
#NOTE! The "models" are for code demonstration purposes only, and have no relation to reality!
#NOTE! DO NOT USE THIS MODULE OR THE CODE IN IT FOR ANY MODELING OR ESTIMATION PURPOSES WHAT-SO-EVER!
import math

def module_default_footprint_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return dict(
    value=( ((NX*NY*NZ)/(number_processes_X*number_processes_Y*number_processes_Z))*number_processes_X*number_processes_Y*number_processes_Z*1.2+((NX*NY*NZ)*timesteps*.00000001) ),
    error_bound=0.5772156649
    unit="kilobyte"
  )

def module_default_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return dict(
    value=( ((NX*NY*NZ)/(number_processes_X*number_processes_Y*number_processes_Z))*timesteps*1.16925 ),
    error_bound=1.618033,
    unit="second"
  )

def timmys_runtime_prediction_function( NX, NY, NZ, timesteps, number_processes_X, number_processes_Y, number_processes_Z ):
  return i_hope_this_is_right_who_knows( NX, NY, NZ, timesteps)

# Do not use --runtime-prediction-function on this function! Use --runtime-prediction-function timmys_runtime_prediction_function
def i_hope_this_is_right_who_knows( x, y, z, T ):
  return dict(
    value=( pow( 1.0001, x*y*z*T ) ),
    error_bound=3.1415962,
    unit="second"
  )
```
