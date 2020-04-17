# 2015-11-10_00_KGo
# weak scaling problem
# periodic boundary condition
# terrain.sine PFL problem
# checked and tested by SKo

if { [llength $argv] < 7 } {
  puts "Usage sinusoidal.tcl <Processes in P> <Processes in Q> <Processes in R> <Size in X> <Size in Y> <Size in Z> <Timesteps> \[Test Name\]"
  exit 1
}

#---------------------------------------------------------
# Import the ParFlow TCL package
#---------------------------------------------------------
lappend auto_path $env(PARFLOW_DIR)/bin
package require parflow
namespace import Parflow::*

pfset FileVersion 4

#---------------------------------------------------------
# Global Variables and Input Arguments
#---------------------------------------------------------

set NP [lindex $argv 0]
set NQ [lindex $argv 1]
set NR [lindex $argv 2]
set NX [lindex $argv 3]
set NY [lindex $argv 4]
set NZ [lindex $argv 5]
set NT [lindex $argv 6]

if { [llength $argv] == 8 } {
  set runname [lindex $argv 7]
} else {
  set runname sinusoidal.cpu
}

set DX 1.0
set DY 1.0
set DZ 0.5

set MX           50
set MY           50
set MZ           40

#---------------------------------------------------------
# Process Topology
#---------------------------------------------------------

pfset Process.Topology.P $NP
pfset Process.Topology.Q $NQ
pfset Process.Topology.R $NR

#---------------------------------------------------------
# Computational Grid
#---------------------------------------------------------

pfset ComputationalGrid.Lower.X  0.0
pfset ComputationalGrid.Lower.Y  0.0
pfset ComputationalGrid.Lower.Z  0.0

pfset ComputationalGrid.NX       $NX
pfset ComputationalGrid.NY       $NY
pfset ComputationalGrid.NZ       $NZ

pfset ComputationalGrid.DX       $DX
pfset ComputationalGrid.DY       $DY
pfset ComputationalGrid.DZ       $DZ

#---------------------------------------------------------
# Use p4est software for adaptive mesh refinement
#---------------------------------------------------------
# pfset use_pforest                               "yes"

#---------------------------------------------------------
# Computational SubGrid dims
#---------------------------------------------------------

pfset ComputationalSubgrid.MX                    $MX
pfset ComputationalSubgrid.MY                    $MY
pfset ComputationalSubgrid.MZ                    $MZ

#---------------------------------------------------------
# The Names of the GeomInputs
#---------------------------------------------------------

pfset GeomInput.Names                 "domaininput"

pfset GeomInput.domaininput.GeomName  domain
pfset GeomInput.domaininput.InputType  Box

#---------------------------------------------------------
# Domain Geometry
#---------------------------------------------------------

pfset Geom.domain.Lower.X                        0.0
pfset Geom.domain.Lower.Y                        0.0
pfset Geom.domain.Lower.Z                        0.0

pfset Geom.domain.Upper.X                   [ expr $NX*$DX ]
pfset Geom.domain.Upper.Y                   [ expr $NY*$DY ]
pfset Geom.domain.Upper.Z                   [ expr $NZ*$DZ ]
pfset Geom.domain.Patches             "x-lower x-upper y-lower y-upper z-lower z-upper"

#--------------------------------------------
# variable dz assignments
#------------------------------------------

#pfset Solver.Nonlinear.VariableDz     True
pfset Solver.Nonlinear.VariableDz     False
#pfset dzScale.GeomNames            domain
#pfset dzScale.Type            nzList
#pfset dzScale.nzListNumber       10
#pfset Cell.0.dzScale.Value 1.0
#pfset Cell.1.dzScale.Value 1.0
#pfset Cell.2.dzScale.Value 1.0
#pfset Cell.3.dzScale.Value 1.0
#pfset Cell.4.dzScale.Value 1.0
#pfset Cell.5.dzScale.Value 1.0
#pfset Cell.6.dzScale.Value 1.0
#pfset Cell.7.dzScale.Value 1.0
#pfset Cell.8.dzScale.Value 1.0
#pfset Cell.9.dzScale.Value 1.0

#-----------------------------------------------------------------------------
# Perm
#-----------------------------------------------------------------------------

pfset Geom.Perm.Names                 "domain"

# Values in m/hour

pfset Geom.domain.Perm.Type            Constant
pfset Geom.domain.Perm.Value           0.25

pfset Perm.TensorType               TensorByGeom

pfset Geom.Perm.TensorByGeom.Names  "domain"

pfset Geom.domain.Perm.TensorValX  1.0d0
pfset Geom.domain.Perm.TensorValY  1.0d0
pfset Geom.domain.Perm.TensorValZ  1.0d0

#-----------------------------------------------------------------------------
# Specific Storage
#-----------------------------------------------------------------------------

pfset SpecificStorage.Type            Constant
pfset SpecificStorage.GeomNames       "domain"
pfset Geom.domain.SpecificStorage.Value 1.0e-4
#pfset Geom.domain.SpecificStorage.Value 0.0

#-----------------------------------------------------------------------------
# Phases
#-----------------------------------------------------------------------------

pfset Phase.Names "water"

pfset Phase.water.Density.Type              Constant
pfset Phase.water.Density.Value             1.0

pfset Phase.water.Viscosity.Type    Constant
pfset Phase.water.Viscosity.Value   1.0

#-----------------------------------------------------------------------------
# Contaminants
#-----------------------------------------------------------------------------

pfset Contaminants.Names                    ""

#-----------------------------------------------------------------------------
# Retardation
#-----------------------------------------------------------------------------

pfset Geom.Retardation.GeomNames           ""

#-----------------------------------------------------------------------------
# Gravity
#-----------------------------------------------------------------------------

pfset Gravity                               1.0

#-----------------------------------------------------------------------------
# Setup timing info [hr]
# dt=30min, simulation time=1d, output interval=1h, no restart
#-----------------------------------------------------------------------------

pfset TimingInfo.BaseUnit        1.0
pfset TimingInfo.StartCount      0
pfset TimingInfo.StartTime       0
pfset TimingInfo.StopTime        $NT
pfset TimingInfo.DumpInterval    $NT
pfset TimeStep.Type              Constant
pfset TimeStep.Value             1.0

#-----------------------------------------------------------------------------
# Porosity
#-----------------------------------------------------------------------------

pfset Geom.Porosity.GeomNames          "domain"

pfset Geom.domain.Porosity.Type          Constant
pfset Geom.domain.Porosity.Value         0.25

#-----------------------------------------------------------------------------
# Domain
#-----------------------------------------------------------------------------

pfset Domain.GeomName domain

#-----------------------------------------------------------------------------
# Relative Permeability
#-----------------------------------------------------------------------------

pfset Phase.RelPerm.Type               VanGenuchten
pfset Phase.RelPerm.GeomNames          "domain"

pfset Geom.domain.RelPerm.Alpha         1.0
pfset Geom.domain.RelPerm.N             3.

#---------------------------------------------------------
# Saturation
#---------------------------------------------------------

pfset Phase.Saturation.Type              VanGenuchten
pfset Phase.Saturation.GeomNames         "domain"

pfset Geom.domain.Saturation.Alpha        1.0
pfset Geom.domain.Saturation.N            3.
pfset Geom.domain.Saturation.SRes         0.1
pfset Geom.domain.Saturation.SSat         1.0

#-----------------------------------------------------------------------------
# Wells
#-----------------------------------------------------------------------------

pfset Wells.Names                           ""

#-----------------------------------------------------------------------------
# Time Cycles
#-----------------------------------------------------------------------------

pfset Cycle.Names "constant rainrec"
pfset Cycle.constant.Names              "alltime"
pfset Cycle.constant.alltime.Length      1
pfset Cycle.constant.Repeat             -1

# rainfall and recession time periods are defined here
# rain for 1 hour, recession for 3 hours

pfset Cycle.rainrec.Names                 "rain rec"
pfset Cycle.rainrec.rain.Length           1
pfset Cycle.rainrec.rec.Length            3
# repeat indefinitely
pfset Cycle.rainrec.Repeat                -1

#-----------------------------------------------------------------------------
# Boundary Conditions: Pressure
#-----------------------------------------------------------------------------
pfset BCPressure.PatchNames                   [pfget Geom.domain.Patches]

pfset Patch.x-lower.BCPressure.Type                     FluxConst
pfset Patch.x-lower.BCPressure.Cycle                    "constant"
pfset Patch.x-lower.BCPressure.alltime.Value            0.0

pfset Patch.y-lower.BCPressure.Type                     FluxConst
pfset Patch.y-lower.BCPressure.Cycle                    "constant"
pfset Patch.y-lower.BCPressure.alltime.Value            0.0

pfset Patch.z-lower.BCPressure.Type                     FluxConst
pfset Patch.z-lower.BCPressure.Cycle                    "constant"
pfset Patch.z-lower.BCPressure.alltime.Value            0.0

pfset Patch.x-upper.BCPressure.Type                     FluxConst
pfset Patch.x-upper.BCPressure.Cycle                    "constant"
pfset Patch.x-upper.BCPressure.alltime.Value            0.0

pfset Patch.y-upper.BCPressure.Type                     FluxConst
pfset Patch.y-upper.BCPressure.Cycle                    "constant"
pfset Patch.y-upper.BCPressure.alltime.Value            0.0

## overland flow boundary condition with very heavy rainfall then slight ET
pfset Patch.z-upper.BCPressure.Type                     OverlandFlow
#pfset Patch.z-upper.BCPressure.Type                    FluxConst
#pfset Patch.z-upper.BCPressure.Cycle                   "rainrec"
pfset Patch.z-upper.BCPressure.Cycle                    "constant"
pfset Patch.z-upper.BCPressure.rain.Value       -0.0000005
pfset Patch.z-upper.BCPressure.rec.Value        0.00000
pfset Patch.z-upper.BCPressure.alltime.Value            0.00000000

#---------------------------------------------------------
# Topo slopes in x-direction
#---------------------------------------------------------

pfset TopoSlopesX.Type "PredefinedFunction"
#pfset TopoSlopesX.Type "Constant"
pfset TopoSlopesX.GeomNames "domain"
pfset TopoSlopesX.PredefinedFunction "SineCosTopo"

#---------------------------------------------------------
# Topo slopes in y-direction
#---------------------------------------------------------

pfset TopoSlopesY.Type "PredefinedFunction"
#pfset TopoSlopesY.Type "Constant"
pfset TopoSlopesY.GeomNames "domain"
pfset TopoSlopesY.PredefinedFunction "SineCosTopo"

#---------------------------------------------------------
# Mannings coefficient
#---------------------------------------------------------

pfset Mannings.Type "Constant"
pfset Mannings.GeomNames "domain"
pfset Mannings.Geom.domain.Value 5.52e-6

#-----------------------------------------------------------------------------
# Phase sources:
#-----------------------------------------------------------------------------

pfset PhaseSources.water.Type                         Constant
pfset PhaseSources.water.GeomNames                    domain
pfset PhaseSources.water.Geom.domain.Value        0.0

#-----------------------------------------------------------------------------
# Exact solution specification for error calculations
#-----------------------------------------------------------------------------

pfset KnownSolution                                    NoKnownSolution

#-----------------------------------------------------------------------------
# Set solver parameters
#-----------------------------------------------------------------------------

pfset Solver                                             Richards
pfset Solver.MaxIter                                     2500

pfset Solver.TerrainFollowingGrid                        True

pfset Solver.Nonlinear.MaxIter                           50
pfset Solver.Nonlinear.ResidualTol                       1e-3
pfset Solver.Nonlinear.StepTol                           1e-20
pfset Solver.Nonlinear.Globalization                     LineSearch
pfset Solver.Linear.KrylovDimension                      20
pfset  Solver.Drop                                       1E-20
pfset Solver.Nonlinear.EtaChoice                         EtaConstant
pfset Solver.Nonlinear.EtaValue                          0.001
pfset Solver.Nonlinear.UseJacobian                       True
pfset Solver.Linear.Preconditioner                       PFMG
pfset Solver.Linear.Preconditioner.PCMatrixType          FullJacobian
pfset Solver.Nonlinear.PrintFlag			 NoVerbosity

pfset Solver.WriteSiloSubsurfData False
pfset Solver.WriteSiloMask False
pfset Solver.WriteSiloPressure False
pfset Solver.WriteSiloSaturation False
pfset Solver.WriteSiloSlopes False

pfset Solver.PrintSubsurfData False
pfset Solver.PrintMask  False
pfset Solver.PrintPressure False
pfset Solver.PrintSaturation False

pfset Solver.WriteNetCDFSubsurfData False
pfset Solver.WriteNetCDFMask  False
pfset Solver.WriteNetCDFPressure False
pfset Solver.WriteNetCDFSaturation False

pfset Solver.ROMIOhints romio.hints

#---------------------------------------------------------
# Initial conditions: water pressure
#---------------------------------------------------------

# set water table to be at the bottom of the domain, the top layer is initially dry
pfset ICPressure.Type                                   HydroStaticPatch
pfset ICPressure.GeomNames                              domain
pfset Geom.domain.ICPressure.Value                      -10.0

pfset Geom.domain.ICPressure.RefGeom                    domain
pfset Geom.domain.ICPressure.RefPatch                   z-upper

#-----------------------------------------------------------------------------
# Run and Unload the ParFlow output files
#-----------------------------------------------------------------------------

pfwritedb $runname
pfrun $runname
