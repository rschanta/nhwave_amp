from pathlib import Path
import nhwave_amp


def get_package_path():
    return Path(nhwave_amp.__file__).resolve().parent
