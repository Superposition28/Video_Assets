import os
from pathlib import Path
import configparser

def find_or_create_project_ini(start_path=None):
    if start_path is None:
        start_path = Path(__file__).resolve().parent

    current = start_path
    max_levels = 2
    project_ini = None

    for _ in range(max_levels + 1):
        candidate = current / "project.ini"
        if candidate.exists():
            project_ini = candidate
            break
        current = current.parent

    if project_ini is None:
        project_ini = start_path / "project.ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'name': 'MyProject',
            'version': '1.0.0'
        }
        with open(project_ini, 'w') as f:
            config.write(f)
        print(f"[INFO] Created new project.ini at {project_ini}")
    else:
        print(f"[INFO] Found project.ini at {project_ini}")

    return project_ini.resolve()


def create_module_conf(module_name: str, project_ini_path: Path, mode="independent") -> Path:
    """
    Creates a configuration file for the specified module.

    Args:
        module_name (str): The name of the module.
        project_ini_path (Path): The path to the project.ini file.
        mode (str): The mode of the module (default is "independent").

    Returns:
        Path: The path to the created configuration file.
    """
    module_dir = Path(__file__).resolve().parent
    conf_path = module_dir / "conf.ini"

    # Load project config (optional but can be useful later)
    project_config = configparser.ConfigParser()
    project_config.read(project_ini_path)

    # Create config
    conf = configparser.ConfigParser()
    conf['MODULE'] = {
        'module_name': module_name,
        'mode': mode,
        'project_ini_path': str(project_ini_path)
    }

    with open(conf_path, 'w') as f:
        conf.write(f)
    print(f"[INFO] Created conf.ini for module '{module_name}' at {conf_path}")

    return conf_path


# --- Example usage ---
if __name__ == "__main__":
    project_ini = find_or_create_project_ini()
    create_module_conf(module_name="Video", project_ini_path=project_ini, mode="independent")
