import os
import sys



def setup_project_paths():
    dev_mode = os.getenv('PIPE_DEV_MODE') == 'TRUE'
    PROJECT_CODE = os.environ['PROJECT_CODE']
    PIPE_DEV_REPO = os.getenv('PIPE_DEV_REPO')
    DEPT_BASE = os.environ['DEPT_BASE']
    local_show_scripts_directory = None
    if PIPE_DEV_REPO:
        local_show_scripts_directory = f'{PIPE_DEV_REPO}/{PROJECT_CODE}'
    show_scripts_directory = f'{DEPT_BASE}/Rigging/Shows/{PROJECT_CODE}'
    if dev_mode and local_show_scripts_directory and os.path.exists(local_show_scripts_directory):
        os.environ['SHOW_DEV_MODE'] = 'TRUE'
        sys.path.append(local_show_scripts_directory)
        return
    if not os.path.exists(show_scripts_directory):
        raise Exception(f'Show scripts location not found: {show_scripts_directory}')
    sys.path.append(show_scripts_directory)
    __import__(f'{PROJECT_CODE.lower()}_scripts')
