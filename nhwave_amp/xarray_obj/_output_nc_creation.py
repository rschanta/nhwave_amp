import os
import numpy as np
import xarray as xr
import nhwave_amp as fpy
from pathlib import Path
import warnings
from pathlib import Path


def find_prefixes_path(directory):
    '''
    Finds the unique variables output to each RESULT_FOLDER simulation.
    '''
    prefixes = []
    for filename in os.listdir(directory):
        # Split at extension
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
    here, since some variables are 2D and some variables are 3D. Read the 
    relevant lists
    '''
    
    two_d = ['eta_']
    three_d = ['p_','u_','v_','w_']
    
    
    try:
        # READ TIME FILE
        if var_XXXXX.name == 'time_dt.txt':
            return np.loadtxt(var_XXXXX,dtype=np.float32)
        
        # READ 3D FILE
        elif any(var_XXXXX.name.startswith(p) for p in three_d):
            # Read the file
            data = np.loadtxt(var_XXXXX)
            
            # Get expected number of rows
            expected_rows = Kglob * Nglob
            
            # Raise ValueError if dimensions don't work
            if data.shape != (expected_rows, Mglob):
                raise ValueError(f"Unexpected file shape {data.shape}, expected ({expected_rows}, {Mglob})")
            
            # Reshape otherwise
            return data.reshape(Kglob, Nglob, Mglob)
        
        # READ 2D FILE
        elif any(var_XXXXX.name.startswith(p) for p in two_d):
            # Read the file
            data = np.loadtxt(var_XXXXX)
            
            # Get expected number of rows
            expected_rows = Nglob
            
            # Raise ValueError if dimensions don't work
            if data.size != expected_rows * Mglob:
                raise ValueError(f"Unexpected file shape {data.shape}, expected ({expected_rows}, {Mglob})")
                
            # Reshape otherwise
            return data.reshape(Nglob, Mglob)
                
    # Except
    except Exception as e:
        warnings.warn(
            f"Issue reading {var_XXXXX.name} ({e}). Substituting with zeros.",
            UserWarning
        )

        if any(var_XXXXX.name.startswith(p) for p in three_d):
            return np.zeros((Kglob, Nglob, Mglob), dtype=np.float32)
        else:
            return np.zeros((Nglob, Mglob), dtype=np.float32)



    
def load_and_stack_to_tensors(Mglob, Nglob, Kglob, all_var_dict):
    '''
    Load and stack NHWAVE time series outputs into tensors.

    For each variable key in `all_var_dict`, this function loads the associated
    files (using `load_array`), stacks them into a single tensor along a new
    leading axis (time/file index), and returns a dictionary of tensors.
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




def get_into_netcdf(INPUT_NETCDF = None, 
                    RESULT_FOLDER = None,
                    sigma_transform = False):
    
    '''
    This takes all of the outputs of a NHWAVE simulation and compresses them
    to a single NetCDF file with variables in up to 4 dimensions, such as:
        - eta (t_NH,X,Y): Surface profile
        - u   (t_NH,X,Y,sigma_c): Horizontal velocity
        
    As of right now, this does NOT work for station files! 
    
    If the `sigma_transform` is set to true, it will automatically calculate 
    the true z levels of the variables in time and include as a variable 
    Zc
    '''
    
    print('\nStarted compressing raw output files in NetCDF...')

    # Acess the input file
    if not INPUT_NETCDF:
        ptr = fpy.get_key_dirs()
        INPUT_NETCDF = ptr['NC_GLOB_OUT']
        
    # Access the output folder
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

   
    # Get list of all variables found in the result folder
    var_list = find_prefixes_path(RESULT_FOLDER)
    
    # Dictionary with keys for each variable type (eta,u,sta,etc.) and values a sorted list of all files
        # for each one (ie- {'eta': ['eta_00000','eta_00001', 'eta_00002' ...]})
    var_paths = get_vars_out_paths(RESULT_FOLDER, var_list)

    ## Get all outputs
    output_variables = load_and_stack_to_tensors(Mglob,Nglob,Kglob,var_paths)
    
    # Pop off some problematic ones
    for key in ['depth','time']:
        output_variables.pop(key, None)
        
    ## Get time and add
    time_array = np.loadtxt(os.path.join(RESULT_FOLDER,'time')).ravel()
    ds = ds.assign_coords({"t_NH": ("t_NH", time_array)})

    
    ## ADD ALL OUTPUT VARIABLES -----------------------------------------------
    for var_name, var_value in output_variables.items():
        print(f"\tCompressing: {var_name}")
        var_value = np.asarray(var_value)

        ## DEAL WITH 2D VARIABLES ---------------------------------------------
        if var_value.ndim == 3:
            # Ensure correct size
            if var_value.shape == (time_array.size, Nglob, Mglob):
                # Transpose so order of variables is (t_NH, X, Y)
                var_value = np.transpose(var_value, (0, 2, 1))
                # Assign to the dataset
                ds = ds.assign({
                    var_name: (["t_NH", "X", "Y"], var_value)
                })
            else:
                raise ValueError(f"{var_name}: unexpected 2D-with-time shape {var_value.shape}")
        ## [END] DEAL WITH 2D VARIABLES ---------------------------------------


        ## DEAL WITH 3D VARIABLES ---------------------------------------------
        elif var_value.ndim == 4:
            # Ensure correct size
            if var_value.shape == (time_array.size, Kglob, Nglob, Mglob):
                # Transpose so order of variables is (t_NH, X, Y)
                var_value = np.transpose(var_value, (0, 3, 2, 1))
                # Assign to the dataset
                ds = ds.assign({
                    var_name: (["t_NH", "X", "Y","sigma_c"], var_value)
                    })
            else:
                raise ValueError(f"{var_name}: unexpected 3D-with-time shape {var_value.shape}")
        ## [END] DEAL WITH 3D VARIABLES ---------------------------------------
        
        
        ## Warning otherwise
        else:
            warnings.warn(f"Skipping {var_name}: ndim={var_value.ndim}, shape={var_value.shape}", UserWarning)
    ## ADD ALL OUTPUT VARIABLES -----------------------------------------------
        
    
    
    ## INVERSE SIGMA TRANSFORM ------------------------------------------------
    if sigma_transform:
        print('\tComputing z-coordinates at each time step...')
        # Total water depth (relies on broadcasting)
        D  = ds["h"] + ds["eta"]                 
        # Actual z-coordinates
        Zc = ds["sigma_c"] * D - ds["h"]            # (t_NH, sigc, Y, X)
        # Add to dataset
        ds["Zc"] = Zc
        ds["Zc"] = ds["Zc"].transpose("t_NH","X","Y","sigma_c")
    ## [END] INVERSE SIGMA TRANSFORM ------------------------------------------
        
    
    
    # COMPRESS AND SAVE OUT ---------------------------------------------------
    comp = dict(zlib=True, complevel=4)
    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf(INPUT_NETCDF, mode='w', encoding=encoding)
    print(f"Succesfully compressed data to .nc file: {INPUT_NETCDF}")
    # [END] COMPRESS AND SAVE OUT ---------------------------------------------
    
    
    return 
