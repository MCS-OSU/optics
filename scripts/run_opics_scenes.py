import sys, os, argparse
import machine_common_sense as mcs
import yaml, json
from opics_common.launch.eval6_agent import Evaluation6_Agent
from opics_common.launch.utils import get_unity_path
from opics_common.launch.utils import get_config_ini_path
from opics_common.launch.utils import get_level_from_config_ini
from opics_common.launch.opics_run_state import OpicsRunState

from rich import traceback, pretty
import datetime
traceback.install()
pretty.install()

            
def get_scene_type_from_scene_file(path):
    f = open(path, 'r')
    scene_json = json.load(f)
    f.close()
    return  scene_json['goal']['category']
    
def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg_dir', default='../cfg')
    parser.add_argument('--scene_dir', default='undefined')
    parser.add_argument('--controller', default='undefined')
    parser.add_argument('--log_dir', default='logs')
    return parser


def usage():
    print("python run_opics_scene.py --scene_dir <path of json scene dir> --controller mcs|replay --log_dir <non_default_log_dir>")

if __name__ == "__main__":

    if not 'OPICS_HOME' in os.environ:
        print('')
        print("      ERROR - OPICS_HOME not defined.  Please 'export OPICS_HOME=<parent_of_opics_dir>'")
        print('')
        sys.exit()
    
    args       = make_parser().parse_args()
    cfg_dir    = args.cfg_dir
    controller_type = args.controller
    if not controller_type in ['mcs', 'replay']:
        print("ERROR - controller must be 'mcs' or 'replay'")
        usage()
        sys.exit()

    log_dir    = args.log_dir
    scene_dir = args.scene_dir
    if 'undefined' == scene_dir:
        usage()
        sys.exit()

    if not os.path.isdir(scene_dir):
        print(f'scene_dir {scene_dir} does not exist')
        usage()
        sys.exit()

    config_ini_path = get_config_ini_path(cfg_dir)
    
    print(f'...using config_init_path {config_ini_path}')
    
    files = os.listdir(scene_dir)
    for file in files:
        if file.endswith('.json'):
            scene_path = os.path.join(scene_dir, file)
            command = f'python run_opics_scene.py --scene {scene_path} --controller {controller_type} --log_dir {log_dir}'
            os.system(command)
    
