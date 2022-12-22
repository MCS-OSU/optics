import sys, os, argparse
import machine_common_sense as mcs
import yaml, json
from opics.common.launch.eval6_agent import Evaluation6_Agent
from opics.common.launch.utils       import get_config_ini_path
from opics.common.launch.utils       import get_level_from_config_ini
from scripts.opics_run_state         import OpicsRunState
from core.optics_dirs                import SystestDirectories
from core.test_register              import TestRegisterLocal, TestRegisterRemote
from opics.common.constants          import EC2B_HOME, MCS_CONTROLLER, MCS_RECORDING_CONTROLLER, REPLAY_CONTROLLER
from core.optics_spec_loader         import OpticsSpec
from rich                            import traceback, pretty
from pathlib                         import Path
import time
import datetime
traceback.install()
pretty.install()

def create_systest_test_register(optics_spec, manager_proximity):
    if manager_proximity == 'local':  
        home_dir = str(Path.home())
        systest_dirs = SystestDirectories(home_dir, optics_spec)      
    else:
        home_dir = EC2B_HOME
        systest_dirs = SystestDirectories(home_dir, optics_spec)

    if manager_proximity == 'local':
        # trun  will read and write files directly
        test_register = TestRegisterLocal(systest_dirs)
    else:
        # trun will transact files with ec2b via scp
        test_register = TestRegisterRemote(systest_dirs)
    return test_register


def validate_enum_arg(arg_name, arg, valid_vals):
    if arg not in valid_vals:
        print(f'ERROR - Invalid value for {arg_name}: {arg}')
        usage()
        sys.exit()

def get_scene_type_from_scene_file(path):
    f = open(path, 'r')
    scene_json = json.load(f)
    f.close()
    return  scene_json['goal']['category']
    
def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg_dir', default='../../../cfg')
    parser.add_argument('--scene', default='undefined')
    parser.add_argument('--optics_spec', default='undefined')
    parser.add_argument('--manager_proximity', default='default')
    parser.add_argument('--session_path', default='undefined')
    parser.add_argument('--log_dir', default='undefined')
    return parser


def usage():
    print("python optics_run_scene.py --scene <scene_path>  --optics_spec <optics_spec_path> --log_dir <log_dir> --manager_proximity local|remote --session_path <session_path>")

if __name__ == "__main__":

    if not 'OPICS_HOME' in os.environ:
        print('')
        print("      ERROR - OPICS_HOME not defined.  Please 'export OPICS_HOME=<parent_of_opics_dir>'")
        print('')
        sys.exit()
    
    args       = make_parser().parse_args()
    cfg_dir    = args.cfg_dir

    optics_spec_path = args.optics_spec
    print("trying to open optics spec: ", optics_spec_path)
    optics_spec = OpticsSpec(optics_spec_path)

    project            = optics_spec.proj
    version            = optics_spec.version
    controller_type    = optics_spec.controller
    spec_name          = optics_spec.name
    manager_proximity  = args.manager_proximity
    session_path       = args.session_path
    log_dir            = args.log_dir
    
    validate_enum_arg('controller_type', controller_type, [MCS_CONTROLLER, REPLAY_CONTROLLER, MCS_RECORDING_CONTROLLER])
    validate_enum_arg('project',         project,         ['pvoe', 'inter', 'avoe'])
    validate_enum_arg('manager_proximity',  manager_proximity,  ['local', 'remote'])

    scene_path = args.scene
    if 'undefined' == scene_path:
        usage()
        sys.exit()
    if session_path == 'undefined':
        print('NOTE session_path must be passed in from the calling trun.py script so in case this script senses errors that warrant shutting down trun')
        usage()
        sys.exit()

    config_ini_path = get_config_ini_path(cfg_dir)
    
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
    if level != 'level2':
        print(f'ERROR - level {level} not supported for systest runs - check {config_ini_path}')
        sys.exit()
    print("==================================================================")
    print("")
    print(f"METADATA LEVEL: {level}")
    print("")
    print("==================================================================")
    print("==========================================================================")
    print(f"       running scene {scene_path}")
    print("==========================================================================")
    scene_type = get_scene_type_from_scene_file(scene_path)
    start_time = datetime.datetime.now()

    run_state = OpicsRunState(scene_path)
    tr = create_systest_test_register(optics_spec, manager_proximity)
    # share the session path passed in from trun.py
    tr.set_session_path(session_path)
    
    print(f'   ...using log_dir {log_dir}')

    run_state.set_test_register(tr)
    while run_state.needs_run_attempt():
        run_state.starting_scene()
        agent = Evaluation6_Agent(config_ini_path, level, scene_type, controller_type, run_state)
        if run_state.is_session_pointless():
            print(f'Session is pointless because run_state is {run_state.state}')
            print('Ending session.')
            system.exit()
        if run_state.is_controller_timed_out():
            print('   ...controller likely timed out - waiting 30 sec to try again with new Evaluation6_Agent')
            time.sleep(30)
            continue
        

        agent.run_scene(scene_path, scene_json, log_dir)
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        print(f'...total time for scene {total_time}')

        if run_state.is_session_pointless():
            print(f'Session is pointless because run_state is {run_state.state}')
            print('Ending session.')
            sys.exit()
        elif run_state.should_retry_after_pause():
            print(f'...pausing for {run_state.retry_pause_time} seconds before retrying')
            time.sleep(run_state.retry_pause_time)
