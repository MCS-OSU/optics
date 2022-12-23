import sys, os
from opics.common.logging.scene_logger  import get_scene_name_from_path, get_log_path
from opics.common.launch.utils          import get_unity_path
from opics.common.launch.utils          import get_config_ini_path
from opics.common.launch.utils          import get_level_from_config_ini
from opics.common.constants             import EC2B_HOME
from core.test_register                 import TestRegisterLocal, TestRegisterRemote
from core.optics_dirs                   import SystestDirectories
from core.utils                         import ensure_dirs_exist, remote_ensure_dirs_exist, ensure_dir_exists
from core.utils                         import get_scene_type_from_scene_name
from core.constants                     import NO_MORE_SCENES_TO_RUN
from core.optics_spec_loader            import OpticsSpec

import subprocess

#from rich import traceback, pretty
from pathlib import Path
import datetime
#traceback.install()
#pretty.install()


def find_mcs_log_path(log_root, proj, scene_name):
    scene_type = get_scene_type_from_scene_name(scene_name)
    log_dir = os.path.join(log_root, proj, scene_type)
    # in case old logs left behind, be robust and picj the most recent one
    candidates = []
    for file in os.listdir(log_dir):
        if file.startswith(scene_name):
            candidates.append(os.path.join(log_dir, file))
    if len(candidates) == 0:
        raise Exception(f"ERROR: no log file found for scene {scene_name} in {log_dir}")
    return max(candidates, key=os.path.getctime)

def verify_level2():
    opics_home      = os.environ["OPICS_HOME"]
    config_ini_path = get_config_ini_path(opics_home + '/cfg')
    level           = get_level_from_config_ini(config_ini_path)
    print(f'...using config_init_path {config_ini_path}')
    assert level in ['level2']

class OpticsTestRunner():
    def __init__(self, optics_spec_path, manager_proximity, run_mode):
        verify_level2()
        self.optics_spec_path   = optics_spec_path
        self.optics_spec        = OpticsSpec(optics_spec_path)
        self.manager_proximity  = manager_proximity
        self.controller_type    = self.optics_spec.controller
        self.run_mode           = run_mode
        opics_home              = os.environ["OPICS_HOME"]

        self.configure_tmp_log_dirs()
        self.configure_tmp_scene_file_dir()
        self.configure_systest_dirs()
        self.configure_test_register()

        # create SystestDirectories as approriate
        

        # create TestRegister as appropriate
       

    def configure_tmp_log_dirs(self):
        opics_home               = os.environ["OPICS_HOME"]
        self.optics_scripts_dir = opics_home + '/scripts/optics/scripts' # this is where this script lives
        self.tmp_mcs_log_dir     = self.optics_scripts_dir + '/tmp_mcs_logs'
        self.tmp_stdout_log_dir  = self.optics_scripts_dir + '/tmp_stdout_logs'
        ensure_dir_exists(self.tmp_mcs_log_dir) 
        ensure_dir_exists(self.tmp_stdout_log_dir) 
        print(f'[optics].......tmp log dir - mcs log root {self.tmp_mcs_log_dir}')
        print(f'[optics].......tmp log dir - stdout  {self.tmp_stdout_log_dir}')
        os.makedirs(self.tmp_stdout_log_dir, exist_ok=True)

    def configure_tmp_scene_file_dir(self):
        if self.manager_proximity == 'remote':
            self.scenes_dir = self.optics_scripts_dir + '/scenes_being_run'
            ensure_dir_exists(self.scenes_dir) 

    def configure_systest_dirs(self):
        if self.manager_proximity == 'local':  
            systest_dir_home_dir = str(Path.home())
            self.systest_dirs = SystestDirectories(systest_dir_home_dir, self.optics_spec)      
            print('[optics].......ensuring local directories exist')
            ensure_dirs_exist(self.systest_dirs.get_top_level_dirs())
            print('[optics].......local directories ensured')
        else:
            systest_dir_home_dir = EC2B_HOME
            self.systest_dirs = SystestDirectories(systest_dir_home_dir, self.optics_spec)
            print('[optics].......ensuring remote directories exist')
            remote_ensure_dirs_exist(self.systest_dirs.get_top_level_dirs())
            print('[optics].......remote directories ensured')

    def configure_test_register(self):
        if self.manager_proximity == 'local':
            # trun  will read and write files directly
            self.test_register = TestRegisterLocal(self.systest_dirs)
        else:
            # trun will transact files with ec2b via scp
            self.test_register = TestRegisterRemote(self.systest_dirs)
        self.test_register.register_session(self.optics_spec.version)
        opics_home = os.environ["OPICS_HOME"]
        self.run_dir = os.path.join(opics_home,'scripts','optics','scripts')
        
    def acquire_scene_from_manager(self, run_mode):
        if self.test_register.is_session_killed():
            print('[optics].......session killed, likely due to detected resource constraints')
            sys.exit()
        scene_path = self.test_register.request_job(self.optics_spec.version, run_mode)
        if scene_path == NO_MORE_SCENES_TO_RUN:
            return (NO_MORE_SCENES_TO_RUN, NO_MORE_SCENES_TO_RUN)
        print(f'[optics].......request_job returned scene_path {scene_path}')
        scene_name = get_scene_name_from_path(scene_path)
        print(f'[optics].......derived scene_name {scene_name}')
        return (scene_path, scene_name)

    def ensure_scene_positioned_locally(self, scene_path, scene_name):
        if self.manager_proximity == 'remote':
            # copy scene file to local
            local_scene_path = os.path.join(self.scenes_dir,scene_name+'.json')
            self.test_register.fetch_remote_file(scene_path, local_scene_path)
            return local_scene_path
        return scene_path

    def pass_logs_to_manager(self, mcs_log_path, stdout_log_path):
        print(f'[optics].......mcs_log_path found as {mcs_log_path}') 
        self.test_register.store_scene_log(mcs_log_path)
        self.test_register.store_stdout_log(stdout_log_path)
        os.system(f"rm {stdout_log_path} {mcs_log_path}") # remove the log files after copying them to the register
        
    def pass_video_files_to_manager(self, videos_dir):
        if os.path.exists(videos_dir):
            self.test_register.store_videos(videos_dir)

    def get_video_dir(self, scene_name):
        # mcs controller puts video dir under the current directory
        opics_home = os.environ('OPICS_HOME')
        optics_dir = os.path.join(opics_home, 'scripts', 'optics')
        video_dir  = os.path.join(optics_dir, 'scripts', scene_name)
        print(f'[optics].......video dir determined as {video_dir}')
        return video_dir



    def run(self):
        while True:
            (scene_path, scene_name) = self.acquire_scene_from_manager(self.run_mode)
            if NO_MORE_SCENES_TO_RUN == scene_path:
                print('[optics].......no more scenes to run')
                sys.exit()
            else:
                print(f'[optics].......acquired scene {scene_name} at {scene_path}')
            
            local_scene_path         = self.ensure_scene_positioned_locally(scene_path, scene_name)
            print(f'[optics].......local_scene_path found as {local_scene_path}')
            # configure log names
            stdout_log_path = self.tmp_stdout_log_dir + '/' + scene_name + '_stdout.txt'
            print(f'stdout_path {stdout_log_path}')

            # run the scene
            print('')
            print(f'[optics]...tasked with {scene_path}...')
            run_command = f"cd {self.run_dir};python optics_run_scene.py --scene {local_scene_path} --optics_spec {self.optics_spec_path}  --log_dir {self.tmp_mcs_log_dir} --manager_proximity {self.manager_proximity} --session_path {self.test_register.session_path}  2>&1 | tee {stdout_log_path}"  # redirect stderr to stdout and tee to stdout_logname
            print(f'[optics]....RUN PROFILE: ')
            print(f'[optics].......controller:      {self.controller_type}')
            print(f'[optics].......manager is:      {self.manager_proximity}') 
            print('')
            print(f'[optics].......spec:            {self.optics_spec.name}')
            print(f'[optics].......scene_name:      {scene_name}') 
            print('')
            print(f'[optics].......mcs_log_dir:     {self.tmp_mcs_log_dir}')
            print(f'[optics].......stdout_log_path: {stdout_log_path}')
            print('')
            print('[optics].......running scene...')
            #print(f' attempting command : {run_command}')
            os.system(run_command)
            print('[optics].......scene run complete')
            mcs_log_path = find_mcs_log_path(self.tmp_mcs_log_dir, self.optics_spec.proj, scene_name)
            self.pass_logs_to_manager(mcs_log_path, stdout_log_path)
            print(f'[optics]......checking to see if video dir {scene_name} is present...')
            video_dir = self.get_video_dir(scene_name)
            if os.path.exists(video_dir):
                print(f'[optics]......moving video files to register...')
                self.pass_video_files_to_manager(video_dir)
                print(f'[optics]......removing video dir...')
                os.system(f"rm -rf {video_dir}")
            if self.manager_proximity == 'remote':
                os.system(f"rm {local_scene_path}") # remove the temp copy of the scene just run
            print(f'[optics].......done with {local_scene_path}')

