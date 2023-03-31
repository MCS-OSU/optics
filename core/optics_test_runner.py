import sys, os
from core.test_register        import TestRegisterLocal, TestRegisterRemote
from core.optics_dirs          import SystestDirectories
from core.utils                import get_scene_name_from_path
from core.utils                import ensure_dirs_exist, remote_ensure_dirs_exist, ensure_dir_exists
from core.utils                import get_scene_type_from_scene_name
from core.utils                import optics_info, optics_debug, optics_error, optics_fatal
from core.constants            import NO_MORE_SCENES_TO_RUN
from core.optics_spec_loader   import OpticsSpec
from core.constants            import EC2_MACHINE_HOME

import subprocess

import traceback
#from rich import traceback, pretty
from pathlib import Path
import datetime
# traceback.install()
# pretty.install()


def find_mcs_log_path(log_root, proj, scene_name):
    scene_type = get_scene_type_from_scene_name(scene_name)
    log_dir = os.path.join(log_root, proj, scene_type)
    # in case old logs left behind, be robust and picj the most recent one
    candidates = []
    if proj == 'pvoe':
        for file in os.listdir(log_dir):
            if file.startswith(scene_name) and file.endswith('.log'):
                candidates.append(os.path.join(log_dir, file))
    else:
        for file in os.listdir(log_dir):
            if file.startswith(scene_name):
                candidates.append(os.path.join(log_dir, file))
    if len(candidates) == 0:
        raise Exception(f"ERROR: no log file found for scene {scene_name} in {log_dir}")
    print(f' *************************  log_candidates: {candidates}')
    
    return max(candidates, key=os.path.getctime)


class OpticsTestRunner():
    def __init__(self, optics_spec_path, manager_proximity, run_mode):
        self.optics_spec_path   = optics_spec_path
        self.optics_spec        = OpticsSpec(optics_spec_path)
        self.manager_proximity  = manager_proximity
        self.controller_type    = self.optics_spec.controller
        self.run_mode           = run_mode
        self.optics_home         = os.environ["OPTICS_HOME"]

        self.configure_tmp_log_dirs()
        self.configure_tmp_scene_file_dir()
        self.configure_systest_dirs()
        self.configure_test_register()

        # create SystestDirectories as approriate
        

        # create TestRegister as appropriate
       

    def configure_tmp_log_dirs(self):
        #if 'pvoe' == self.optics_spec.proj:
        self.optics_scripts_dir = self.optics_home + '/scripts'
        #else:
        #    self.optics_scripts_dir = opics_home + '/scripts/optics/scripts' # this is where this script lives
        self.tmp_mcs_log_dir     = self.optics_scripts_dir + '/tmp_mcs_logs'
        self.tmp_stdout_log_dir  = self.optics_scripts_dir + '/tmp_stdout_logs'
        ensure_dir_exists(self.tmp_mcs_log_dir) 
        ensure_dir_exists(self.tmp_stdout_log_dir) 
        optics_debug(f'tmp log dir - mcs log root {self.tmp_mcs_log_dir}')
        optics_debug(f'tmp log dir - stdout  {self.tmp_stdout_log_dir}')
        os.makedirs(self.tmp_stdout_log_dir, exist_ok=True)

    def configure_tmp_scene_file_dir(self):
        if self.manager_proximity == 'remote':
            self.scenes_dir = self.optics_scripts_dir + '/scenes_being_run'
            ensure_dir_exists(self.scenes_dir) 

    def configure_systest_dirs(self):
        if self.manager_proximity == 'local':  
            systest_dir_home_dir = str(Path.home())
            self.systest_dirs = SystestDirectories(systest_dir_home_dir, self.optics_spec)      
            optics_debug('ensuring local directories exist')
            ensure_dirs_exist(self.systest_dirs.get_top_level_dirs())
            optics_debug('local directories ensured')
        else:
            systest_dir_home_dir = EC2_MACHINE_HOME
            self.systest_dirs = SystestDirectories(systest_dir_home_dir, self.optics_spec)
            optics_debug('ensuring remote directories exist')
            remote_ensure_dirs_exist(self.systest_dirs.get_top_level_dirs())
            optics_debug('remote directories ensured')

    def configure_test_register(self):
        if self.manager_proximity == 'local':
            # trun  will read and write files directly
            self.test_register = TestRegisterLocal(self.systest_dirs)
        else:
            # trun will transact files with ec2b via scp
            self.test_register = TestRegisterRemote(self.systest_dirs)
        self.test_register.register_session(self.optics_spec.version)
        # NOTE(Mazen): ec2a testing
        self.run_dir = os.path.join(self.optics_home,'scripts')
        
    def acquire_scene_from_manager(self, run_mode):
        if self.test_register.is_session_killed():
            optics_info('session killed, likely due to detected resource constraints')
            sys.exit()
        scene_path = self.test_register.request_job(self.optics_spec.version, run_mode)
        optics_debug(f'request_job returned scene_path: {scene_path}')
        if scene_path == NO_MORE_SCENES_TO_RUN:
            return (NO_MORE_SCENES_TO_RUN, NO_MORE_SCENES_TO_RUN)
        scene_name = get_scene_name_from_path(scene_path)
        optics_debug(f'derived scene_name {scene_name}')
        return (scene_path, scene_name)

    def ensure_scene_positioned_locally(self, scene_path, scene_name):
        if self.manager_proximity == 'remote':
            # copy scene file to local
            local_scene_path = os.path.join(self.scenes_dir,scene_name+'.json')
            self.test_register.fetch_remote_file(scene_path, local_scene_path)
            return local_scene_path
        return scene_path

    def pass_logs_to_manager(self, mcs_log_path, stdout_log_path):
        optics_info('passing logs to manager')
        self.test_register.store_scene_log(mcs_log_path)
        self.test_register.store_stdout_log(stdout_log_path)
        os.system(f"rm {stdout_log_path} {mcs_log_path}") # remove the log files after copying them to the register
        
    def pass_video_files_to_manager(self, videos_dir):
        if os.path.exists(videos_dir):
            self.test_register.store_videos(videos_dir)

    def get_video_dir(self, scene_name):
        # mcs controller puts video dir under the current directory
        video_dir  = os.path.join(self.optics_home, 'scripts', scene_name)
        optics_debug(f'video dir determined as {video_dir}')
        return video_dir

    def print_summary_of_run(self, scene_path, scene_name, stdout_log_path):
        optics_info('')
        optics_info(f'tasked with {scene_name}...')
        optics_info(f'RUN PROFILE: ')
        optics_info(f'....controller:      {self.controller_type}')
        optics_info(f'....manager is:      {self.manager_proximity}') 
        optics_debug('')
        optics_info(f'....spec:            {self.optics_spec.name}')
        optics_debug('')
        optics_debug(f'....mcs_log_dir:     {self.tmp_mcs_log_dir}')
        optics_debug(f'....stdout_log_path: {stdout_log_path}')
        optics_debug('')
        optics_info(f'....running scene...')

    def save_logs(self, scene_name, stdout_log_path):
        mcs_log_path = find_mcs_log_path(self.tmp_mcs_log_dir, self.optics_spec.proj, scene_name)
        self.pass_logs_to_manager(mcs_log_path, stdout_log_path)

    def save_videos(self, scene_name):
        optics_debug(f'checking to see if video dir {scene_name} is present...')
        if self.optics_spec.save_videos:
            video_dir = self.get_video_dir(scene_name)
            if os.path.exists(video_dir):
                optics_info(f'passing videos to manager...')
                self.pass_video_files_to_manager(video_dir)
                optics_debug(f'removing video dir...')
                os.system(f"rm -rf {video_dir}")

    def run(self):
        next_todo = 'run_loop'
        while True:
            try:
                next_todo = 'acquire_scene_from_manager'
                optics_debug(f'starting run loop iteration...')
                (scene_path, scene_name) = self.acquire_scene_from_manager(self.run_mode)
                if NO_MORE_SCENES_TO_RUN == scene_path:
                    optics_fatal('no more scenes to run')
                else:
                    optics_info(f'acquired scene {scene_name}')
                
                next_todo = 'ensure_scene_positioned_locally'
                local_scene_path         = self.ensure_scene_positioned_locally(scene_path, scene_name)
                optics_debug(f'local_scene_path found as {local_scene_path}')
                # configure log names
                stdout_log_path = self.tmp_stdout_log_dir + '/' + scene_name + '_stdout.txt'
               
                # run the scene
                next_todo = 'launch_scene'
                self.print_summary_of_run(scene_path, scene_name, stdout_log_path)
                scene_type = get_scene_type_from_scene_name(scene_name)
                logger_path_dir = os.path.join(self.tmp_mcs_log_dir, self.optics_spec.proj, scene_type)
                run_command = f"cd {self.run_dir};LOGGER_PATH={logger_path_dir} python optics_run_scene.py --scene {local_scene_path} --optics_spec {self.optics_spec_path}  --log_dir {self.tmp_mcs_log_dir} --manager_proximity {self.manager_proximity} --session_path {self.test_register.session_path}  2>&1 | tee {stdout_log_path}"  # redirect stderr to stdout and tee to stdout_logname
                optics_debug(f'run command: {run_command}')
                os.system(run_command)
                optics_debug('scene run complete')

                # save info to register
                next_todo = 'save_logs'
                self.save_logs(scene_name, stdout_log_path)
                next_todo = 'save_videoa'
                self.save_videos(scene_name)
                
                # cleanup temp files
                next_todo = 'cleanup_temp_files'
                if self.manager_proximity == 'remote':
                    os.system(f"rm {local_scene_path}") # remove the temp copy of the scene just run
                optics_info(f'{scene_name} COMPLETED')
            except Exception as err:
                optics_error(f'exception in OpticsTestRunner.run() + {err}')
                optics_error(f'failed at step {next_todo}')
                if next_todo == 'acquire_scene_from_manager':
                    sys.exit()
                traceback.format_exc()
                

