#!/usr/bin/env python3

import re, os, sys, argparse, json, shutil, importlib.util, inspect, pprint
import subprocess as sp
import fileinput as fi

GLOBAL_DEBUG = False

pfrun_ouput_guards = "HOPEFULLY UNIQUE PREAMBLE THAT BLOCKS OFF VALID JSON CODE FROM OUTPUT"

pfrun_redefinition_code = r"""
proc Parflow::pfrun { runname args } {
  puts [format "pfrun %s has been intercepted by the size determination script." [format $runname $args]]

  set time_units  [pfget TimingInfo.BaseUnit]
  set start_time [pfget TimingInfo.StartTime]
  set stop_time [pfget TimingInfo.StopTime]
  set time_delta [expr $stop_time - $start_time]
  set time_steps [expr $time_delta / $time_units]

  set NX [pfget ComputationalGrid.NX]
  set NY [pfget ComputationalGrid.NY]
  set NZ [pfget ComputationalGrid.NZ]
  set NP [pfget Process.Topology.P]
  set NQ [pfget Process.Topology.Q]
  set NR [pfget Process.Topology.R]

  puts [format \
"
""" \
+ pfrun_ouput_guards + \
r"""
{
  \"grid\" :
  {
    \"NX\" : %s,
    \"NY\" : %s,
    \"NZ\" : %s
  },
  \"time\" : {
    \"time_steps\" : %s
  },
  \"process_topology\" : {
    \"NP\" : %s,
    \"NQ\" : %s,
    \"NR\" : %s
  }
}
""" \
+ pfrun_ouput_guards + \
r"""
" $NX $NY $NZ $time_steps $NP $NQ $NR]
}
"""

namespace_rx = re.compile( r"namespace\s+import\s+Parflow::\*" )
package_rx = re.compile( r"package\s+require\s+parflow" )
output_rx = re.compile( pfrun_ouput_guards + r"(?P<JSON_data>.+)" + pfrun_ouput_guards, flags=re.DOTALL )

def print_error(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

class ClobberError(RuntimeError):
  def __init__(this, path):
    this.path = path

  def __str__(this):
    return f"Path {path} already exists."

class NoNamespaceImportLocationError(RuntimeError):
  def __init__(this):
    pass
  def __str__(this):
    return f"Could not find Parflow namespace import conforming to the regular expression {namespace_rx.pattern}  to insert new pfrun definition."

class FailedScriptExecutionError(RuntimeError):
  def __init__(this, command_list, stdout, stderr, exit_code ):
    this.command_list = command_list
    this.stdout = stdout
    this.stderr = stderr
    this.exit_code = exit_code
  def __str__(this):
    return "Script command \"" + (" ".join( this.command_list ) ) + f" failed with exit code {this.exit_code}.\np\nStandard Output:\n{this.stdout}\n\nStandard Error:\n{this.stderr}"

class InvalidScriptOutputError(RuntimeError):
  def __init__(this, output):
    this.output = output

  def __str__(this):
    return "Invalid output from script:\n" + "".join( ( '\t'+line for line in this.output ) ) + "\n"

class UnimplementedPredictionError(RuntimeError):
  def __init__(this, output):
    pass
  def __str__(this):
    return "Failed to find any valid prediction functions in analysis_module."

class InvalidPredictionValueError(RuntimeError):
  def __init__(this, value, reason, function_name=None):
    this.value = value
    this.reason = reason
    this.function_name = function_name

  def __str__(this):
    if this.function_name == None:
      return f"Prediction function produced an invalid value:\n\t{this.reason}\n\tstr: "+str(this.value)+"\n\trepr: "+str(repr(this.value)) + "\n"
    else:
      return f"Prediction function \"{this.function_name}\" produced an invalid value:\n\t{this.reason}\n\tstr: "+str(this.value)+"\n\trepr: "+str(repr(this.value)) + "\n"

class PredictionFunctionException(RuntimeError):
  def __init__(this, expt, function_name=None):
    this.expt = expt
    this.function_name = function_name

  def __str__(this):
    if this.function_name == None:
      return f"There was an exception during the execution of a user defined function:\n{this.expt}"
    else:
      return f"There was an exception during the execution of user defined function \"{this.function_name}\":\t\n{this.expt}"

def move_file( src_path, dest_path, clobber=False ):
  if not clobber and os.path.exists( dest_path ):
    raise ClobberError( dest_path )

  shutil.move( src_path, dest_path )


def write_file( output_file_path, output_text, clobber=False ):
  if not clobber and os.path.exists(output_file_path):
    raise ClobberError( output_file_path )

  with open( output_file_path, "w" ) as output_file:
    output_file.write( output_text )

def parse_tcl_file( file_name ):
  lines = []
  require_line = None
  namespace_line = None
  pfrun_invocations = []

  for (index,line) in enumerate( fi.input( file_name ) ):
    lines.append( line )

    if package_rx.search( line ) != None:
      if require_line != None:
        print_error( f"Warning! Re-requiring package on line {index} (previously {require_line})." )
      require_line = index

    if namespace_rx.search( line ) != None:
      if namespace_line != None:
        print_error( f"Warning! Re-importing namespace on line {index} (previously {namespace_line})." )
      namespace_line = index

    if r"pfrun" in line:
      pfrun_invocations.append( index )

  # The namespace invocation is mandatory
  if namespace_line == None:
    raise NoNamespaceImportLocationError()

  return {
    "contents": lines,
    "require_line"  : require_line,
    "namespace_line"  : namespace_line,
    "pfrun_invocations" : pfrun_invocations
    }


def convert_tcl_script( contents, require_line, namespace_line, pfrun_invocations ):
  new_contents = []


  for (index, line) in enumerate(contents):
    new_contents.append( line )
    if index == namespace_line:
      new_contents.append( pfrun_redefinition_code )

  return new_contents


def parse_and_convert_file( input_file_path ):
  data = parse_tcl_file( input_file_path )

  new_content = convert_tcl_script( data["contents"], data["require_line"], data["namespace_line"], data["pfrun_invocations"] )
  # Fileinput preserves line-endings
  new_text = "".join(new_content)
  if GLOBAL_DEBUG:
    print_error("="*50 + f"\nNew Script\n" + "-"*50 + f"\n{new_text}\n" + "="*50)
  return new_text


def process_file( input_file_path, output_file_path, clobber=False ):
  text = parse_and_convert_file( input_file_path )
  write_file( output_file_path, text, clobber )


def run_script( script_path, arguments, tcl_shell="tclsh", exact_command=False ):

  if exact_command:
    command = arguments
  else:
    command = [tcl_shell, script_path, *arguments]
  process = sp.Popen( command , stdout=sp.PIPE, stderr=sp.PIPE)

  stdout, stderr = process.communicate()

  exit_status = process.wait()

  stdout = stdout.decode("utf-8")
  stderr = stderr.decode("utf-8")
  if GLOBAL_DEBUG:
    print_error( f"> {' '.join(command)}\nStandard Output:\n{stdout}\n\nStandard Error:\n{stderr}" )

  if exit_status != 0:
    raise FailedScriptExecutionError( command, stdout, stderr, exit_status )

  return stdout

def parse_script_output( output_text ):
  m = output_rx.search( output_text)
  if m == None:
    raise InvalidScriptOutputError( output_text )
  json_data = json.loads( m.group("JSON_data") )
  return json_data


def process_script( script_path, arguments, tcl_shell="tclsh", exact_command=False ):
  output = run_script( script_path, arguments, tcl_shell, exact_command )
  json_data = parse_script_output( output )
  return json_data


def is_legal_footprint_prediction_value( value ):
  if value == None:
    return {"condition" : False, "reason" : "Value is None" }
  if type(value) not in [int, float]:
    return {"condition" : False, "reason" : f"Value is not numerical ({type(value)})" }
  if float(value) < 0.0:
    return {"condition" : False, "reason" : "Value less than 0.0" }
  return {"condition" : True, "reason": None}


def is_legal_runtime_prediction_value( value ):
  if value == None:
    return {"condition" : False, "reason" : "Value is None" }
  if type(value) not in [int, float]:
    return {"condition" : False, "reason" : f"Value is not numerical ({type(value)})" }
  if float(value) < 0.0:
    return {"condition" : False, "reason" : "Value less than 0.0" }
  return {"condition" : True, "reason": None}


def predict( data, prediction_function, value_check_function ):
  nx=data["grid"]["NX"]
  ny=data["grid"]["NY"]
  nz=data["grid"]["NZ"]
  timesteps=data["time"]["time_steps"]
  np=data["process_topology"]["NP"]
  nq=data["process_topology"]["NQ"]
  nr=data["process_topology"]["NR"]

  try:
    prediction_value = prediction_function( nx, ny, nz, timesteps, np, nq, nr)
  except Exception as expt:
    raise PredictionFunctionException(expt, prediction_function.__name__)

  check = value_check_function(prediction_value)
  if not check["condition"]:
    raise InvalidPredictionValueError(prediction_value, check["reason"], prediction_function.__name__)

  return prediction_value


def write_json( output_file_path, data, clobber=False ):
  if not clobber and os.path.exists(output_file_path):
    raise ClobberError( output_file_path )

  with open( output_file_path, "w" ) as output_file:
    json.dump( data, output_file )


def format_report( data ):
  return pprint.pformat( data, width=-1, compact=True )

exit_codes = {
  "success" : 0,
  "internal_error" : -1,
  "command_line_error" : -2,
  "clobber_error" : -3,
  "prediction_error" : -4,
  "prediction_module_error" : -5,
  "script_parse_error" : -6
}


def main( argv=sys.argv ):
  script_root_path = os.path.abspath( os.path.dirname( argv[0] ) )

  global GLOBAL_DEBUG

  report_format = dict(
    estimation = dict(
      footprint = dict(
        value = "float",
        units = "string"
      ),
      runtime = dict(
        value = "float",
        units = "string"
      )
    ),
    configuration = dict(
      grid = dict(
        NX = "int",
        NY = "int",
        NZ = "int"
      ),
      time = dict(
        time_steps = "float"
      ),
      process_topology = dict(
        NP = "int",
        NQ = "int",
        NR = "int"
      )
    )
  )

  default_generated_script_suffix=".size_determination.output.tcl"
  default_backup_suffix=".size_determination.automated_backup.original.tcl"
  default_tcl_shell = "tclsh"
  default_prediction_module = script_root_path+"/default_prediction_module.py"
  default_footprint_prediction_function = "footprint_prediction_function"
  default_runtime_prediction_function  = "runtime_prediction_function"

  report_format_string = "Report JSON format:\n" + "".join( ( f"\t{line}\n" for line in format_report( report_format ).split("\n") ) )
  exit_code_string = "Exit codes:\n" + "".join( ( f"\t{name}: {code}\n" for (name, code) in exit_codes.items() ) )

  epilog=f"{report_format_string}\n{exit_code_string}"

  parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,epilog=epilog)

  parser.add_argument(
    "file_path",
    type=str,
    help="Path to input tcl script."
  )

  parser.add_argument(
    "execution_arguments",
    type=str,
    nargs="*",
    default="",
    help="Arguments necessary to execute tcl script, if any."
  )
  parser.add_argument(
    "--exact-command",
    # metavar="exact_command",
    action="store_true",
    default=False,
    help="Execution arguments will be interpreted as the exact execution command without any modifications or additions."
  )
  parser.add_argument(
    "--no-execute",
    # metavar="allow_clobber",
    action="store_true",
    default=False,
    help="Disables execution of generated script and prediction of runtime and footprint."
  )
  parser.add_argument(
    "--tcl-shell",
    # metavar="tcl_shell",
    type=str,
    default=default_tcl_shell,
    help=f"Command used to execute tcl scripts. (Default: {default_tcl_shell})"
  )

  parser.add_argument(
    "--generated-script-path",
    # metavar="generated_script_path"
    type=str,
    default=None,
    help=f"Name of output file. (Default: <file_path>{default_generated_script_suffix})" #Note suffix variable already has . separator
  )

  parser.add_argument(
  "--generated-script-suffix",
  type=str,
  default=default_generated_script_suffix,
  help=f"Specify suffix for creating the path of new script file generated by this tool.- Default: {default_generated_script_suffix}"
  )

  parser.add_argument(
    "--backup-suffix",
    # metavar="backup_suffix",
    type=str,
    default=default_backup_suffix,
    help=f"Suffix used when --in-place-generation set without exact path. (Default: {default_backup_suffix})"
  )
  parser.add_argument(
    "--in-place-generation",
    # metavar="in_place_generation",
    type=str,
    nargs='?',
    default=False, #Note: states are False if unset, None if set with no argument, and some str value if set with argument
    # action="store_true",
    help=f"Enables in-place generation of new script. Instead of writing generated script to a new location, makes backup of input script and writes generated script to <file_path>. Optional argument BACKUP_PATH specifies exact path to place backup of input script. Default: <file_path>{default_backup_suffix}"  #Note suffix variable already has . separator
  )
  parser.add_argument(
    "--allow-clobber",
    # metavar="allow_clobber",
    action="store_true",
    default=False,
    help="Allows overwriting of existing files."
  )

  parser.add_argument(
    "--prediction-module",
    # metavar="prediction_module",
    type=str,
    default=default_prediction_module,
    help=f"Set path to prediction module. (Default: {default_prediction_module})"
  )
  parser.add_argument(
    "--footprint-prediction-function",
    # metavar="footprint_prediction_function",
    type=str,
    default="footprint_prediction_function",
    help=f"Set function from prediction module to use to predict ParFlow footprint (Default: \"{default_footprint_prediction_function}\")"
  )
  parser.add_argument(
    "--runtime-prediction-function",
    # metavar="runtime_prediction_function",
    type=str,
    default="runtime_prediction_function",
    help=f"set function from prediction module to use to predict ParFlow footprint (Default: \"{default_runtime_prediction_function}\")"
  )

  parser.add_argument(
    "--report-output",
    # metavar="report_output",
    type=str,
    default=None,
    help="Specify path to write report output to instead of standard out."
  )

  parser.add_argument(
    "--debug",
    default=False,
    action="store_true",
    help="Enable debugging output in tool."
  )

  args = parser.parse_args( argv[1:] )

  GLOBAL_DEBUG=args.debug

  # First, check that CLI arguments are at least correct
  setup_is_correct = True

  if args.in_place_generation and args.generated_script_path:
    print_error( "Error: Cannot use --generated-script-path and --in-place-generation flags simultaneously.")
    setup_is_correct = False

  if args.file_path == args.generated_script_path:
    print_error( "Error: input and output cannot be same file. Use --in-place-generation flag instead.")
    setup_is_correct = False


  # Exit if CLI arguments are incorrect
  if not setup_is_correct:
    print_error("There were errors from command line flag usage.")
    print_error("Please check usage.")
    parser.print_help(file=sys.stderr)
    return exit_codes["command_line_error"]


  if not args.no_execute:
    # Setup application
    # Load prediction module
    args.prediction_module = os.path.abspath(args.prediction_module)
    spec = importlib.util.spec_from_file_location("", args.prediction_module)
    prediction_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prediction_module)

    module_dict = dict( inspect.getmembers(prediction_module) )

    footprint_prediction_function = None
    runtime_prediction_function = None

    if args.footprint_prediction_function in module_dict:
      footprint_prediction_function = module_dict[args.footprint_prediction_function]
    else:
      print_error( f"Error: Prediction module ({args.prediction_module}) lacks the required function \"{args.footprint_prediction_function}\".")
      return exit_codes["prediction_module_error"]

    if args.runtime_prediction_function in module_dict:
      runtime_prediction_function = module_dict[args.runtime_prediction_function]
    else:
      print_error( f"Error: Prediction module ({args.prediction_module}) lacks the required function \"{args.runtime_prediction_function}\".")
      return exit_codes["prediction_module_error"]


  # if the output is not explicitly defined use
  if args.generated_script_path == None:
    args.generated_script_path = args.file_path + args.generated_script_suffix

  # If --in-place-generation enabled, move files and setup new input/output paths
  if args.in_place_generation != False:
    # if set with no args in_place_generation == None
    if args.in_place_generation == None:
      backup_path = args.file_path + args.backup_suffix
    # if set with args in_place_generation is the specified backup path
    else:
      backup_path = args.in_place_generation

    try:
      move_file( args.file_path, backup_path, args.allow_clobber )
    except ClobberError as expt:
      if expt.path == backup_path:
        print_error( f"Error: destination for backup ({backup_path}) already exists.\nEither move existing file, or use --allow-clobber option." )
      else:
        print_error( f"UNEXPECTED Error: During backup the following path exists causing a ClobberError:\n\t{expt.path}\nOffending path is *NOT* backup_path ({backup_path}).\nThis error is unexpected.\nPlease contact developers.\n(HIGHLY RISKY SUGGESTION) Either move existing file, or use --allow-clobber option." )
      return exit_codes["clobber_error"]

    args.generated_script_path = args.file_path
    args.file_path = backup_path

  # Process file, including writing
  try:
    process_file( args.file_path, args.generated_script_path, args.allow_clobber )
  except ClobberError as expt:
    if expt.path == args.generated_script_path:
      print_error( f"Error: destination for output ({args.generated_script_path}) already exists.\nEither move existing file, or use --allow-clobber option." )
    else:
      print_error( f"UNEXPECTED Error: During processing the following path exists causing a ClobberError:\n\t{expt.path}\nOffending path is *NOT* args.generated_script_path ({args.generated_script_path}).\nThis error is unexpected.\nPlease contact developers.\n(HIGHLY RISKY SUGGESTION) Either move existing file, or use --allow-clobber option." )
    return exit_codes["clobber_error"]
  except NoNamespaceImportLocationError as expt:
    print_error( f"Error: during script parsing." )
    print_error( expt )
    return exit_code["script_parse_error"]

  if not args.no_execute:
    # Execute file
    try:
      script_output = process_script( args.generated_script_path, args.execution_arguments, args.tcl_shell, args.exact_command )
    except Exception as expt:
      print_error( f"Error: Exception caught during scrip processing:" )
      print_error( expt )
      return exit_codes["internal_error"]

    # Estimate memory footprint
    try:
      predicted_footprint = predict( script_output, footprint_prediction_function, is_legal_footprint_prediction_value )
    except InvalidPredictionValueError as expt:
      print_error( f"Error: footprint prediction function ({args.footprint_prediction_function}) produced invalid value." )
      print_error( expt )
      return exit_codes["prediction_error"]
    except PredictionFunctionException as expt:
      print_error( f"Error: during execution of footprint prediction function ({args.footprint_prediction_function})" )
      print_error( expt )
      return exit_codes["prediction_error"]

    # Estimate runtime
    try:
      predicted_runtime = predict( script_output, runtime_prediction_function, is_legal_runtime_prediction_value )
    except InvalidPredictionValueError as expt:
      print_error( f"Error: runtime prediction function ({args.runtime_prediction_function}) produced invalid value." )
      print_error( expt )
      return exit_codes["prediction_error"]
    except PredictionFunctionException as expt:
      print_error( f"Error: during execution of runtime prediction function ({args.runtime_prediction_function})" )
      print_error( expt )
      return exit_codes["prediction_error"]

    # create JSONified report and either print to stdout or write to file
    report = dict(
      estimation = dict(
        footprint = dict(
          value = predicted_footprint,
          units = "kilobyte"
        ),
        runtime = dict(
          value = predicted_runtime,
          units = "seconds"
        )
      ),
      configuration = script_output
    )

    # Write/print report
    if args.report_output != None:
      try:
       write_json( args.report_output, report, args.allow_clobber )
      except ClobberError as expt:
        if expt.path == args.report_output:
          print_error( f"Error: destination for json output ({args.report_output}) already exists.\nEither move existing file, or use --allow-clobber option." )
        else:
          print_error( f"""UNEXPECTED Error: During backup the following path exists causing a ClobberError:\n\t{expt.path}\nOffending path is *NOT* args.report_output ({args.report_output}).\nThis error is unexpected.\nPlease contact developers.\n(HIGHLY RISKY SUGGESTION) Either move existing file, or use --allow-clobber option.""" )
    else:
      print( format_report( report ) )

  return exit_codes["success"]

if __name__ == "__main__":
  main()
