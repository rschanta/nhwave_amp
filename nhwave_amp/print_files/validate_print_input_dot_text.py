
import copy
import numpy as np


def get_defaulted_requirements():
    '''
    These are parameters that NHWAVE needs at runtime, since the io functions
    there expect all of these to be present. However, not all of them will be
    explicitly relevant for all simulations. So default values are assumed to
    simply ensure that the model doesn't crash. These should always be checked
    before running.
    
    '''
    return {
        
    # GRID TYPE
     "IVGRD": 
         {"default": "1", 
          "desc": "type of vertical grid. 1 = uniform, 2 = exp. spacing"},
    "RGRID": 
        {"default": "1", 
         "desc": "grid size increment for IVGRID = 2"}, 
        
    # TIMING / OUTPUT CONTROL
    "PLOT_START":
        {"default": 0.0,
         "desc": "time to start writing plot output"},
    
    "SCREEN_INTV":
        {"default": 5.0,
         "desc": "interval between screen messages"},
    
    "HOTSTART":
        {"default": "F",
         "desc": "enable hotstart / restart capability"},
    
    
    
    "DT_INI":
    {"default": "0.1",
     "desc": "initial time step"},

    "DT_MIN":
        {"default": "1e-05",
         "desc": "minimum allowable time step"},
    
    "DT_MAX":
        {"default": "0.1",
         "desc": "maximum allowable time step"},
    
    "SIM_STEPS":
        {"default": "1000000",
         "desc": "total number of simulation steps"},
        
    
    # STABILITY / NUMERICS
    "CFL":
        {"default": 0.5,
         "desc": "CFL number"},
    
    "VISCOUS_NUMBER":
        {"default": 0.1666666,
         "desc": "viscous time-stepping"},
    
    "FROUDE_CAP":
        {"default": 10.0,
         "desc": "Maximum Fr"},
    
    "MinDep":
        {"default": 0.01,
         "desc": "minimum water depth"},
    
    
    # TURBULENCE STUFF ========================================================
    "IVTURB":
        {"default": 999,
         "desc": "vertical eddy viscosity choice"},
    
    "IHTURB":
        {"default": 999,
         "desc": "horizontal eddy viscosity choice"},
    
    "PRODTYPE":
        {"default": 0,
         "desc": "shear production option"},
    "RNG":
        {"default": "F",
         "desc": "RNG k-epsilon model Yakhot et al"},
    # [END] TURBULENCE STUFF ==================================================
    

    "VISCOSITY":
        {"default": 1e-6,
         "desc": "kinematic viscosity"},
    
    "Schmidt":
        {"default": 1.0,
         "desc": "Schmidt number"},
    
    "Cvs":
        {"default": 0.0,
         "desc": "Constant vertical eddy viscosity"},
    
    "Chs":
        {"default": 0.0,
         "desc": "Constant horizontal eddy viscosity"},
    
    
    # TURBULENCE MODEL OPTIONS

    # 
    "DEPTH_TYPE":
        {"default": "CELL_CENTER",
         "desc": "h(x,y) defined at centers"},
        
    "ANA_BATHY":
        {"default": "F",
         "desc": "Use user-defined bathymetry"},
    
    "DepConst":
        {"default": "0.0",
         "desc": "(seems to be deprecated)"},
    
    "INITIAL_EUVW":
        {"default": "F",
         "desc": "HOT START CONDITION"},
    
    "Ibot":
        {"default": "1",
         "desc": "1 = Cd0 type friction, 2 = Zob type friction"},
    
    "Cd0":
        {"default": "0.0",
         "desc": "Bottom roughness coefficient"},
    
    "Zob":
        {"default": "0.0",
         "desc": "Bottom roughness length"},
    
    
    ## WIND ===================================================================
    "Iws":
        {"default": "YES",
         "desc": "1 = constant wind, 2 = spatial wind via wind.txt"},
    
    "WindU":
        {"default": "0.0",
         "desc": "Constant wind speed in x"},
    
    "WindV":
        {"default": "0.0",
         "desc": "Constant wind speed in y"},
    ## [END] WIND =============================================================
    
    
    "slat":
        {"default": "0.0",
         "desc": "Latitude for Coriolis"},
    
    ## MODEL TYPE =============================================================
    "BAROTROPIC":
        {"default": "T",
         "desc": "T = Barotropic, F = Baroclinic"},
    
    "NON_HYDRO":
        {"default": "T",
         "desc": "T = Nonhydrostatic, F = hydrostatic (pressure solver)"},
    ## [END] MODEL TYPE =======================================================
    
    

    "HLLC":
        {"default": "T",
         "desc": "T = HLLC, F = HLL scheme"},
    
    "TRAMP":
        {"default": "0.0",
         "desc": "Model ramp up"},
    
 
    ## SERIAL SOLVER FLAGS ====================================================
    "ISOLVER":
        {"default": "2",
         "desc": "[SERIAL] 1 (CG), 2 (GMRES-IC3), 3 (GMRES-SOR3)"},
    
    "ITMAX":
        {"default": "1000",
         "desc": "[SERIAL] 1 (CG), 2 (GMRES-IC3), 3 (GMRES-SOR3)"},
    
    "TOL":
        {"default": "YES",
         "desc": "[SERIAL] Solver tolerance "},
    ## [END] SERIAL SOLVER FLAGS ==============================================
    
    
    
    ## PERIODIC IN X AND Y ====================================================
    "PERIODIC_X":
        {"default": "F",
         "desc": "if T, Mglob must be power of 2"},
    
    "PERIODIC_Y":
        {"default": "F",
         "desc": "if T, Mglob must be power of 2"},
    ## [END] PERIODIC IN X AND Y ==============================================
    
    
    ## BOUNDARY CONDITIONS ====================================================
    "BC_X0":
        {"default": "1",
         "desc": "Left boundary condition in x (1- free slip)"},
    
    "BC_Xn":
        {"default": "1",
         "desc": "Right boundary condition in x (1- free slip)"},
    
    "BC_Y0":
        {"default": "1",
         "desc": "Left boundary condition in y (1- free slip)"},
    
    "BC_Yn":
        {"default": "1",
         "desc": "Right boundary condition in y (1- free slip)"},
    
    "BC_Z0":
        {"default": "1",
         "desc": "Boundary condition at bottom (1- free slip)"},
    
    "BC_Zn":
        {"default": "YES",
         "desc": "Boundary condition at top (1- free slip)"},
    ## [END] BOUNDARY CONDITIONS ==============================================
    
    
    ## RHEOLOGY
    "RHEOLOGY_ON":
        {"default": "F",
         "desc": "Flag for rheology"},
    "Yield_Stress":
        {"default": "0.0",
         "desc": "[RHEOLOGY] Yield stress"},
    "Plastic_Visc":
        {"default": "0.0",
         "desc": "[RHEOLOGY] Plastic viscosity"},
    

    ## STATION OUTPUTS 
    "NSTAT":
        {"default": "0.0",
         "desc": "Number of stations (if >0, need gage file)"},
    "PLOT_INTV_STAT":
        {"default": "10.0",
         "desc": "time resolution of stations"},
        
        
    ## EXTERNAL FORCING
    "EXTERNAL_FORCING":
        {"default": "T",
         "desc": "Flag for external forcing"},
    "Pgrad0":
        {"default": "0.0",
         "desc": "Open-channel flow like x-forcing"},

    
    # WAVE AVERAGING ==========================================================
    "WAVE_AVERAGE_ON":
        {"default": "F",
         "desc": "toggle wave-averaged output"},
    
    "WAVE_AVERAGE_START":
        {"default": "0.0",
         "desc": "time to start wave averaging"},
    
    "WAVE_AVERAGE_END":
        {"default": "0.0",
         "desc": "time to end wave averaging"},
    
    "WaveheightID":
        {"default": "1",
         "desc": "1 = Mean, 2 = RMS"},
    # [END] WAVE AVERAGING ====================================================
    
    
    
    # TRUE OUTPUTS
        "OUT_H": 
            {"default": "T", 
             "desc": "output water depth"}, 
        "OUT_E":
            {"default": "T", 
             "desc": "output surface elevation"}, 
        "OUT_U":
            {"default": "T", 
             "desc": "output x-velocity"},
        "OUT_V":
            {"default": "T",
             "desc": "output y-velocity"},
        "OUT_W":
            {"default": "T",
             "desc": "output z-velocity"},
        "OUT_P":
            {"default": "T",
             "desc": "output dynamic pressure"},
    # FALSE OUTPUTS    
        "OUT_K":
            {"default": "F",
             "desc": "output turbulent kinetic energy"},
        "OUT_D":
            {"default": "F",
             "desc": "output turbulent dissipation rate"},
        "OUT_S":
            {"default": "F",
             "desc": "output salinity"},
        "OUT_C":
            {"default": "F",
             "desc": "output eddy viscosity"},
        "OUT_B":
            {"default": "F",
             "desc": "output bubble void fraction"},
        "OUT_A":
            {"default": "F",
             "desc": "output Reynolds Stress"},
        "OUT_F":
            {"default": "F",
             "desc": "output sediment concentration"},
        "OUT_T":
            {"default": "F",
             "desc": "output bottom shear stress"},
        "OUT_G":
            {"default": "F",
             "desc": "output bed elevation"},
        "OUT_I":
            {"default": "F",
             "desc": "output salinity"},
        "OUT_Z":
            {"default": "F",
             "desc": "output varying-depth"},
        "OUT_M":
            {"default": "F",
             "desc": "output maximum height"},
        
                }


def get_required_params():
    '''
    These are parameters that are required for any reasonable simulation, so 
    an error will be thrown if they are not in the input dictionary. Note that
    NHWAVE needs a pretty large list of parameters to run, but many of them can
    have reasonable default values if not specified. 
    
    See `get_defaulted_requirements` for the parameters that will assume
    reasonable default values if not otherwise given.
    '''
    return {
# BASIC GEOMETRY    
    # Grid size
        "DX" : "grid size in x",
        "DY" : "grid size in y",
    # Number of points in each dimension
        "Mglob" : "number of points in x",
        "Nglob" : "number of points in y",
        "Kglob" : "number of sigma-coordinate layers",
    # MPI Topology splitting
        "PX" : "number of processors for x domain split",
        "PY" : "number of processors for y domain split",
    # TIMING
        "TOTAL_TIME": "total simulation time",
        "PLOT_INTV": "interval between plot outputs",
    # TURBULENCE
        "VISCOUS_FLOW": "enable turbulence"
        }

# Helper to check if missing
def is_missing(x):
        if x is None:
            return True
        if isinstance(x, (float, np.floating)) and np.isnan(x):
            return True
        return False


def validate_nhwave_params(var_dict, strict=False):
    """
    Checks that required parameters exist.

    strict=True:
        Any missing parameter -> STOP.

    strict=False:
        Missing non-hard-required parameter ->
            prints NOTE with default from CSV.
        If no default exists -> STOP.
    """

    ## Copy the dict
    d = copy.deepcopy(var_dict)
    
    ## Get the hard requirements and the defaulted requirements
    defaults = get_defaulted_requirements()
    hard_required = get_required_params()

    # Get keys present in both
    keys_to_check = set(defaults.keys()) | set(hard_required.keys())

    # Loop through all the keys
    for k in sorted(keys_to_check):

        ## CHECK THAT VARIABLE EXISTS
        if k in var_dict:
            # Ensure that it's actually filled in
            if is_missing(var_dict[k]):
                present = False
            else:
                present = True
        # Return false if it's not present
        else:
            present = False
        # Skip the loop if the variable is truly present
        if present:
            continue


        # DEAL WITH MISSING
        if strict:
            # Strict flag: everything must be specified!
            desc = hard_required.get(k, defaults.get(k, {}).get("desc", ""))
            raise ValueError(f"\tSTOP: {k} ({desc}) must be specified!")
        
        if k in hard_required:
            # Hard requirement: must specify!
            desc = hard_required[k]
            raise ValueError(f"\tSTOP: {k} ({desc}) must be specified!")
        
        if k in defaults:
            # Default: sub in here!
            default_value = defaults[k]["default"]
            desc = defaults[k].get("desc", "")
            print(
                f"\tNOTE: {k} ({desc}) not specified, using default: {default_value}")
            d[k] = default_value
    print('Passed initial checks of parameters!')
    return d


