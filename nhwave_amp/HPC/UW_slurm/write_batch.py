from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os
import nhwave_amp as nh



def write_batch(template_name = None,
                mode_name = 'UW_slurm',
                params = None,
                name = None,
                other_params = None):
    
    # Get environment variables
    slurm_path = os.getenv('SLURM_FILES')
    log_path   = os.getenv('SLURM_LOGS')
    
    
    
    # MAKE LOG FOLDER(S)  -----------------------------------------------------
    # Array jobs
    if "array" in params:
        # Output files
        out_log_dir = os.path.join(log_path,'OUT')
        os.makedirs(out_log_dir,exist_ok=True)
        params['output'] = os.path.join(out_log_dir,'out_%a.out')
        # Error Files
        err_log_dir = os.path.join(log_path,'ERR')
        os.makedirs(err_log_dir,exist_ok=True)
        params['error'] = os.path.join(out_log_dir,'err_%a.out')
    # Non-array jobs
    else:
        params['output'] = os.path.join(log_path,'out.out')
        params['error'] = os.path.join(log_path,'err.out')
    # [END] MAKE LOG FOLDER(S)  -----------------------------------------------
    
    
    # Add on other parameters
    if other_params:
        params = {**params, **other_params}
    params['job-name'] = name
        
    ## CONSTRUCT FILE FROM TEMPLATE -------------------------------------------
    # Path to the nhwave_amp module
    path  = nh.get_package_path()
    # Path to the template folder
    template_dir = path / "HPC" / mode_name / "templates"
    
    # Load the template
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    # Get the template
    template = env.get_template(template_name)
    
    # Render the template
    rendered = template.render(**params)
    # Construct path to batch files
    batch_name = os.path.join(slurm_path,f'{name}.qs')
    # Write the file
    Path(batch_name).write_text(rendered)
    ## [END] CONSTRUCT FILE FROM TEMPLATE -------------------------------------
    return batch_name


    