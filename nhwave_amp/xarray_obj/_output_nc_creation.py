import os
import numpy as np
import xarray as xr
import nhwave_amp as fpy
from pathlib import Path
import warnings
from pathlib import Path
from typing import Dict, List

def find_prefixes_path(directory):
    '''
    Finds the unique variables output to each RESULT_FOLDER simulation. This
    assumes files of the form name_XXXXX for each time step.
    '''
    prefixes = []
    for filename in os.listdir(directory):
        
        # Skip hidden files or other artifacts
        if filename.startswith('.'):
            continue
        
        # Split at filename at extension
        name, _ = os.path.splitext(filename)
        
        # Identify time step files (ends in XXXXX)
        if name[-5:].isdigit() and len(name) > 5:
            variable_ = name[:-5]
        # Identify station files (ends in XXXX)
        elif name[-4:].isdigit() and len(name) > 4:
            variable_ = name[:-4]
        # Identify non time-step files
        else:
            variable_ = name
        # Append to list
        prefixes.append(variable_)

    # Remove duplicates
    prefix_list = list(set(prefixes))
    return prefix_list


def get_var_out_paths(RESULT_FOLDER: Path, var: str) -> list[Path]:
    '''
    Gets a list of paths to all of the output files in RESULT_FOLDER that have 
    names that begin with the string specified by `var`. For example, use `eta_` 
    to get the eta files.
    
    ARGUMENTS:
        - var (str): substring to search for at the beginning of file names. 
            Best to use up to last underscore (ie- `eta_`, `U_undertow`) to 
            avoid issues with similarly named variables
    RETURNS: 
        -path_of_vars (List(Path)): all the paths to the variables 
            searched for

    '''
    out_XXXXX_path = Path(RESULT_FOLDER)
    var_files = []
    for file in out_XXXXX_path.iterdir():
        if file.name.startswith('.'):
            continue
        if file.name.startswith(var):
            var_files.append(file)
                
    path_of_vars = sorted(var_files, key=lambda p: p.name)            
    return path_of_vars

def get_vars_out_paths(RESULT_FOLDER: Path, var_search: list[str])-> Dict[str,list[Path]]:
    '''
    Applies `get_var_in_path` to the path specified for the variables 
    specified in var_search to output a dictionary of path lists. Cleans up 
    name a bit (trailing _)
    
    ARGUMENTS:
        - out_XXXXX (Path): Path to out_XXXXX file
    RETURNS: 
        - var_search (List[str]): list of substrings for `get_var_output_paths`
    '''
    
    all_var_paths = {}
    for var in var_search:
        varname = var[:-1] if var.endswith('_') else var  # Remove trailing _ if they exist
        all_var_paths[varname] = get_var_out_paths(RESULT_FOLDER,var)
    return all_var_paths



def load_array(var_XXXXX: Path, 
               Mglob: int, Nglob: int, Kglob: int):
    '''
    Load a NHWAVE output file into a NumPy array. Note that these are all ASCII
    arrays stored in basic text. The dimensionality of variables is important
    here, since some variables are 2D and some variables are 3D. These are 
    explicitly defined in the lists at the beginning of the function.
    
    The time_dt.txt file is a special file that is read in separately.
    '''
    
    two_d = ['eta_']
    three_d = ['p_','u_','v_','w_','k_','c_','d_']
    
    
    try:
        # READ TIME FILE ------------------------------------------------------
        if var_XXXXX.name == 'time_dt.txt':
            '''
            The time file is special, since there's only one of them and its a 
            simple column file.
            '''
            return np.loadtxt(var_XXXXX,dtype=np.float32)
        # [END] READ TIME FILE ------------------------------------------------
        
        
        # READ 3D FILE --------------------------------------------------------
        elif any(var_XXXXX.name.startswith(_) for _ in three_d):
            '''
            The conditional here is a generator expression that checks if the
            var_XXXXX file is a variable defined in the three_d list. These
            variables will have (Kglob * Nglob) rows and Mglob columns.
            '''
            
            # Read the file
            data = np.loadtxt(var_XXXXX)
            
            # Get expected number of rows
            expected_rows = Kglob * Nglob
            
            # Raise ValueError if dimensions don't work
            if data.shape != (expected_rows, Mglob):
                raise ValueError(f"Unexpected file shape {data.shape}, expected ({expected_rows}, {Mglob})")
            
            # Reshape otherwise
            return data.reshape(Kglob, Nglob, Mglob)
        # [END] READ 3D FILE --------------------------------------------------
        
        
        # READ 2D FILE --------------------------------------------------------
        elif any(var_XXXXX.name.startswith(p) for p in two_d):
            '''
            The conditional here is a generator expression that checks if the
            var_XXXXX file is a variable defined in the two_d list. These
            variables will have Nglob rows and Mglob columns.
            '''
            # Read the file
            data = np.loadtxt(var_XXXXX)
            
            # Get expected number of rows
            expected_rows = Nglob
            
            # Raise ValueError if dimensions don't work
            if data.size != expected_rows * Mglob:
                raise ValueError(f"Unexpected file shape {data.shape}, expected ({expected_rows}, {Mglob})")
                
            # Reshape otherwise
            return data.reshape(Nglob, Mglob)
        # [END] READ 2D FILE --------------------------------------------------
        
        
    # EXCEPTION ---------------------------------------------------------------
    except Exception as e:
        '''
        This generalically catches any error. If the variable is specified in
        two_d or three_d, it pads in zeroes.
        '''
        
        # Raise a warning
        warnings.warn(
            f"Issue reading {var_XXXXX.name} ({e}). Substituting with zeros.",
            UserWarning
        )

        # Place all zeroes depending on what it's supposed to be
        if any(var_XXXXX.name.startswith(p) for p in three_d):
            return np.zeros((Kglob, Nglob, Mglob), dtype=np.float32)
        elif any(var_XXXXX.name.startswith(p) for p in two_d):
            return np.zeros((Nglob, Mglob), dtype=np.float32)
        else:
            print('No dimension specified for this variable!')
    # [END] EXCEPTION ---------------------------------------------------------
    return

    
def load_and_stack_to_tensors(Mglob, Nglob, Kglob, all_var_dict):
    '''
    Load and stack NHWAVE time series outputs into tensors.

    For each variable key in `all_var_dict`, this function loads the associated
    files (using `load_array`), stacks them into a single tensor along a new
    leading axis (time/file index), and returns a dictionary of tensors.
    
    We need to know the shape of each variable to do this correctly.
    '''


    tensor_dict = {}

    # Loop through all variables found in RESULT_FOLDER
    for var, file_list in all_var_dict.items():
        
        var_arrays = []
        # Loop through all files of this variable and load in
        for file_path in file_list:
            arr = load_array(file_path, Mglob, Nglob, Kglob)
            var_arrays.append(arr)

        try:
            tensor = np.stack(var_arrays, axis=0)  
        except Exception as e:
            print(f"Issue stacking {var}: {e}")
            continue

        tensor_dict[var] = tensor

    return tensor_dict


def append_zero_top_layer(var_value):
    '''
    Append a zero-valued layer onto the last dimension of a 4D array. This is
    used for the pressure.
    
    Example:
        Input shape:  (T, Y, X, K)
        Output shape: (T, Y, X, K+1)
    '''

    # Create zero-valued top layer
    zeros_top = np.zeros(
        (
            var_value.shape[0],
            var_value.shape[1],
            var_value.shape[2],
            1,
        ),
        dtype=var_value.dtype,
    )

    # Append layer onto final axis
    return np.concatenate(
        [var_value, zeros_top],
        axis=3,
    )


def get_into_netcdf(INPUT_NETCDF = None, 
                    RESULT_FOLDER = None,
                    sigma_transform = False,
                    save_out = True):
    
    '''
    This takes all of the outputs of a NHWAVE simulation and compresses them
    to a single NetCDF file with variables in up to 4 dimensions, such as:
        - eta (time,X,Y): Surface profile
        - u   (time,X,Y,sig_c): Horizontal velocity
        - p   (time,X,Y,sig_f): Pressure
    It automatically handles the center/face distinction of velocity and 
    pressure.
    
    If the `sigma_transform` is set to true, it will automatically calculate 
    the true z levels of the variables in time and include as a variable 
    Zc
    '''
    
    print('\nStarted compressing raw output files in NetCDF...')

    # Acess the input file. Read from .env file if not input
    if not INPUT_NETCDF:
        ptr = fpy.get_key_dirs()
        INPUT_NETCDF = ptr['NC_GLOB_OUT']
        
    # Access the output folder. Read from .env file if not input
    if not RESULT_FOLDER:
        ptr = fpy.get_key_dirs()
        RESULT_FOLDER = ptr['RAW_OUT']
        
        
        
    # Load base dataset (created in input phase)
    ds0 = xr.open_dataset(INPUT_NETCDF)
    ds  = ds0.load()
    ds0.close()

    # Dimensions from attrs
    Mglob = int(ds.attrs['Mglob'])
    Nglob = int(ds.attrs['Nglob'])
    Kglob = int(ds.attrs['Kglob'])

   
    # GET LIST OF VARIABLES OUTPUT --------------------------------------------
    '''
    Here, we find what variables actually exist in the output folder. Most 
    variables are stored in the form `name_XXXXX` for each time step, so we
    find all the unique `name`s in the output folder. (var_list)
    
    Then, for each variable, we construct a dictionary for all of its 
    corresponding files. The key is the variable name and the value is a list
    of all the files. For example, for eta, we have:
        {'eta': ['eta_00000','eta_00001', 'eta_00002' ...]}
    This is the var_paths variable
    
    output_variables
    '''
    # List of all variables found
    var_list = find_prefixes_path(RESULT_FOLDER)
    # Paths to all individual output files
    var_paths = get_vars_out_paths(RESULT_FOLDER, var_list)
    # [END] GET LIST OF VARIABLES OUTPUT --------------------------------------
    
    
    ## LOAD IN ALL OUTPUTS ----------------------------------------------------
    '''
    This does the heavy lifting of actually loading in every single file in
    the output folder. `output_variables` is one giant tensor for each variable
    across all time, that will be reshaped appropriately later.
    
    The time is weird and its a TODO currently to fix whatever is wrong with
    this that necessitates this patch.
    '''
    ## Get all outputs
    output_variables = load_and_stack_to_tensors(Mglob,Nglob,Kglob,var_paths)
    
    
    # Pop off some problematic ones
    for key in ['depth','time']:
        output_variables.pop(key, None)
        
    ## Get time and add
    print(os.path.join(RESULT_FOLDER,'time'))
    time_array = np.loadtxt(os.path.join(RESULT_FOLDER,'time')).ravel()
    ds = ds.assign_coords({"time": ("time", time_array)})
    
    ## [END] LOAD IN ALL OUTPUTS ----------------------------------------------
    
    
    
    ## ADD ALL OUTPUT VARIABLES -----------------------------------------------
    '''
    Now, we start loading things into xarray for the final data compression,
    reshaping in sensible ways.
    '''

    for var_name, var_value in output_variables.items():
        
        # Ensure we are a numpy tensor
        var_value = np.asarray(var_value)
        
        # Print some useful checks
        print(f"\tCompressing: {var_name}")
        print(f"\t\t{var_name}: shape={var_value.shape}")
        print(f"\t\ttime_array.size={time_array.size}, Nglob={Nglob}, Mglob={Mglob}")
        if var_name in var_paths:
            print(f"\t\tn_files for {var_name} = {len(var_paths[var_name])}")
            
            
        ## DEAL WITH 2D VARIABLES ---------------------------------------------
        if var_value.ndim == 3:
            '''
            Here, we deal with every 2D variable. This is most likely just 
            eta and potentially depth files.
            '''
            # Ensure correct size
            if var_value.shape == (time_array.size, Nglob, Mglob):
                # Transpose so order of variables is (time, x, y)
                var_value = np.transpose(var_value, (0, 2, 1))
                # Assign to the dataset
                ds = ds.assign({
                    var_name: (["time", "x", "y"], var_value)
                })
            else:
                raise ValueError(f"{var_name}: unexpected 2D-with-time shape {var_value.shape}")
        ## [END] DEAL WITH 2D VARIABLES ---------------------------------------


        ## DEAL WITH 3D VARIABLES ---------------------------------------------
        elif var_value.ndim == 4:
            '''
            Here, we deal with 3D variables. Pressure is stored at the cell
            interfaces whereas everything else is stored at cell interfaces.
            We need to handle them separately.
            '''
            
            ## CELL-CENTERED VALUES--------------------------------------------
            if var_name != 'p':
                '''
                Variables at cell centers. These use sig_c for their vertical
                coordinate.
                '''
                
                # Ensure correct size
                if var_value.shape == (time_array.size, Kglob, Nglob, Mglob):
                    # Transpose so order of variables is (time, x, y, sig_c)
                    var_value = np.transpose(var_value, (0, 3, 2, 1))
                    # Assign to the dataset using sig_f in the vertical
                    ds = ds.assign({
                        var_name: (["time", "x", "y","sig_c"], var_value)
                        })
                else:
                    raise ValueError(f"{var_name}: unexpected 3D-with-time shape {var_value.shape}")
            ## [END] CELL-CENTERED VALUES--------------------------------------
                 
            
            ## PRESSURE -------------------------------------------------------
            elif var_name == 'p':
                '''
                Here, we deal with pressure explicitly, which is stored at the
                bottom cell faces. We also add in the 0 boundary condition at
                the top for completeness. Pressure uses sig_f for its vertical
                coordinate.
                '''
                
                # Ensure correct size
                if var_value.shape == (time_array.size, Kglob, Nglob, Mglob):
                    # Transpose so order of variables is (time, x, y)
                    var_value = np.transpose(var_value, (0, 3, 2, 1))
                    # Add on boundary condition of 0
                    var_value = append_zero_top_layer(var_value)
                    # Assign to dataset using sig_f in the vertical
                    ds = ds.assign({
                        var_name: (["time", "x", "y","sig_f"], var_value)
                        })
                else:
                    raise ValueError(f"{var_name}: unexpected pressure shape {var_value.shape}")
            ## [END] PRESSURE -------------------------------------------------
        ## [END] DEAL WITH 3D VARIABLES ---------------------------------------
        
        
        ## Warning for weird dimensions
        else:
            warnings.warn(f"Skipping {var_name}: ndim={var_value.ndim}, shape={var_value.shape}", UserWarning)
    ## ADD ALL OUTPUT VARIABLES -----------------------------------------------
        
    
    
    ## INVERSE SIGMA TRANSFORM ------------------------------------------------
    if sigma_transform:
        '''
        If requested, calculate the real z-coordinates all the sigma coordinates
        at each time step, creating new data variables z_c and z_f for each
        time step. 
        
        Note that this can't really be a coordinate variable since they change
        at every single time step.
        '''
        print('\tInverting sigma-transform to calculate z-values at each step')
        
        # Total water depth (relies on broadcasting)
        D  = ds["h"] + ds["eta"]                 
        
        # Cell center z values
        ds["z_c"] = (ds["sig_c"] * D - ds["h"]).transpose("time", "x", "y", "sig_c")
        # Cell interfacial z values
        ds["z_f"] = (ds["sig_f"] * D - ds["h"]).transpose("time", "x", "y", "sig_f")

        print('\tFinished inverse coordinate transform!')
    ## [END] INVERSE SIGMA TRANSFORM ------------------------------------------
        
    
    
    # COMPRESS AND SAVE OUT ---------------------------------------------------
    if save_out:
        comp = dict(zlib=True, complevel=4)
        encoding = {var: comp for var in ds.data_vars}
        ds.to_netcdf(INPUT_NETCDF, mode='w', encoding=encoding)
        print(f"Succesfully compressed data to .nc file: {INPUT_NETCDF}")
    # [END] COMPRESS AND SAVE OUT ---------------------------------------------
    
    
    return ds
