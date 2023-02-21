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
    parser.add_argument('--scene', default='undefined')
    parser.add_argument('--controller', default='mcs')
    parser.add_argument('--log_dir', default='default')
    return parser



def usage():
    print("python run_opics_scene.py --scene <path of json scene file> --controller mcs|replay --log_dir <non_default_log_dir")

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
    scene_path = args.scene
    if 'undefined' == scene_path:
        usage()
        sys.exit()

    config_ini_path = get_config_ini_path(cfg_dir)
    
    print(f'...using config_init_path {config_ini_path}')
    

    try:
        scene_json = mcs.load_scene_json_file(scene_path)
    except FileNotFoundError:
        print(f"Error : scene file {scene_path} not found")
        sys.exit()
    except Exception as err:
        print(f"problem with scene file {scene_path} : {err} ")
        sys.exit()

    if scene_json == {}:
        print("Scene Config is Empty", scene_path)
        sys.exit()
    
    level = get_level_from_config_ini(config_ini_path)    
    print("==================================================================")
    print("")
    print(f"METADATA LEVEL: {level}")
    print("")
    print("==================================================================")
    assert level in ['oracle', 'level2']

    print("==========================================================================")
    print(f"       running scene {scene_path}")
    print("==========================================================================")
    scene_type = get_scene_type_from_scene_file(scene_path)

    start_time = datetime.datetime.now()
    run_state = OpicsRunState(scene_path)
    run_state.starting_scene()
    agent = Evaluation6_Agent(config_ini_path, level, controller_type, scene_type,run_state)
    agent.run_scene(scene_path, scene_json, log_dir)
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f'...total time for scene {total_time}')

 
