from importlib.util import set_loader
import os, time, sys
import core.utils as utils
from opics_common.scene_type.type_constants import get_abbrev_scene_type_from_filename
from opics_common.launch.opics_run_state        import NOT_ATTEMPTED, IN_PROGRESS_SCENE_ASSIGNED, OpicsRunState
from core.constants                 import JOB_REQUEST, JOB_REQUEST_SMOKE, JOB_ASSIGN, NO_MORE_SCENES_TO_RUN, SESSION_KILLED, SMOKE_TEST
from core.constants                 import TEST_HISTORY_FIRST_LINE_PREFIX
from core.optics_session            import OpticsSession
from optics_results.scene_state_history    import SceneStateHistory
from core.utils                     import optics_info, optics_error, optics_debug, optics_fatal


class TestRegisterLocal():
    def __init__(self, systest_dirs):
        self.systest_dirs = systest_dirs
        self.has_requested_job = False

    ##########################################################################
    # api used by OpticsTestRunner and OpicsRunState
    ##########################################################################
    def derive_session_path(self, spec_name_sans_proj):
        t = int(time.time())
        machine = os.uname()[1]
        session_filename = f'runner_session_{spec_name_sans_proj}_{machine}_{t}.txt'
        self.session_path = os.path.join(self.systest_dirs.sessions_dir, session_filename)
        # optics_info(f'registering session')
        # utils.add_last_line(self.session_path, session_start_string)

    def is_session_killed(self):
        session_path = self.session_path
        last_line = utils.get_last_line(session_path)
        if 'SESSION_KILLED' in last_line:
            return True
        return False

    def set_session_path(self, session_path):
        # this is needed because run_optics_scene.py needs the session_path to be passed in as an argument by  optics_test_runner.py. 
        # i.e. optics_test_runner.py calls derive_session_path to set it initially, and then needs to pass that derived path in full the
        # run_optics_script that it calls 
        self.session_path = session_path

    def request_job(self, proj, run_mode):
        machine = os.uname()[1]
        if run_mode == SMOKE_TEST: 
            request = JOB_REQUEST_SMOKE
        else:
            request = JOB_REQUEST
        job_request = utils.get_register_control_message(request, proj)
        optics_info(f'requesting job')
        # utils.add_last_line(self.session_path, job_request) Keeping this commented out for now.  updated code is yet to be tested
        if not self.has_requested_job:
            t = int(time.time())
            machine = os.uname()[1]
            session_start_string = f'# trun_session;{proj};{machine};{t}'
            utils.add_last_line(self.session_path, session_start_string)
            utils.add_last_line(self.session_path, job_request)
            self.has_requested_job = True
        else: 
            utils.add_last_line(self.session_path, job_request)

        scene_path = self.await_job_assign_from_tman(machine, self.session_path, 3, 1.5)
        optics_info(f'got job: {scene_path}')
        return scene_path


    def await_job_assign_from_tman(self, requesting_machine, session_path, tries, sleep_time):
        for i in range(tries):
            time.sleep(sleep_time)
            optics_info('(checking for response job request)')
            last_line = utils.get_last_line(session_path)
            if NO_MORE_SCENES_TO_RUN in last_line:
                return NO_MORE_SCENES_TO_RUN
            if JOB_ASSIGN in last_line:
                designated_machine, _, scene_path = utils.parse_job_assign(last_line)
                if designated_machine == requesting_machine:
                    return scene_path
        optics_error(f'no response from tman on JOB_REQUEST')
        optics_error('Check to make sure tman.py is running.')
        sys.exit(1)


    def note_scene_state(self, scene_path, state):
        state_dir = self.systest_dirs.scene_state_dir
        scene_name = os.path.basename(scene_path).split('.')[0]
        optics_debug(f'scene {scene_name} set to state {state}')
        state_path = utils.get_state_path_for_scene_path(scene_path, state_dir)
        utils.add_last_line(state_path, utils.get_register_status_message(state))
        if 'SESSION_FATAL' in state:
            self.note_session_fatal(scene_path)


    def note_session_fatal(self, scene_path):
        session_path = self.session_path
        utils.add_last_line(session_path, utils.get_session_message('SESSION_KILLED'))


    def store_scene_log(self, log_path):
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = get_abbrev_scene_type_from_filename(log_name)
        dest_path = os.path.join(self.systest_dirs.result_logs_dir, scene_type, log_file)
        optics_info(f'storing mcs log')
        utils.ensure_dir_exists(os.path.dirname(dest_path))
        os.system(f' cp {log_path} {dest_path}')


    def store_stdout_log(self, log_path):
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = get_abbrev_scene_type_from_filename(log_name)
        dest_path = os.path.join(self.systest_dirs.stdout_logs_dir, scene_type, log_file)
        optics_info(f'storing stdout log')
        utils.ensure_dir_exists(os.path.dirname(dest_path))
        os.system(f' cp {log_path} {dest_path}')



    def store_videos(self, videos_dir_path):
        # videos_dir == scene_name
        optics_info(f'storing videos {videos_dir_path}')
        videos_dir = os.path.basename(videos_dir_path)
        optics_info(f'videos_dir obtained as {videos_dir}')
        scene_type = get_abbrev_scene_type_from_filename(videos_dir)
        print(f'scene_type obtained as {scene_type}')
        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'topdown')
        optics_info(f'src path {src}')
        optics_info(f'dest path {dest}')
        utils.ensure_dir_exists(os.path.dirname(dest))
        optics_info(f'after ensure dir exists for dest')
        os.system(f' cp {src} {dest}')
        optics_info('copied topdown')
        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'visual')
        os.system(f' cp {src} {dest}')
        optics_info('copied visual')
        # abstaining from storing depth and segmentation videos as per Rajesh request
        # (src, dest) = utils.get_pathnames_for_video(videos_dir, scene_type, self.systest_dirs.videos_dir, 'depth')
        # os.system(f' cp {src} {dest}')

        # (src, dest) = utils.get_pathnames_for_video(videos_dir, scene_type, self.systest_dirs.videos_dir, 'segmentation')
        # os.system(f' cp {src} {dest}')


    ##########################################################################
    # api used by manager
    ##########################################################################

    def init_scene_state_files(self, scene_paths):
        optics_debug('initialize scene state files...')
        for scene_path in scene_paths:
            scene_fname = os.path.basename(scene_path)
            scene_name = scene_fname.split('.')[0]
            state_file_path = utils.get_state_path_for_scene_path(scene_path, self.systest_dirs.scene_state_dir)
            optics_debug(f'state_file_path needed: {state_file_path}')
            utils.ensure_dir_exists(os.path.dirname(state_file_path))
            if not os.path.exists(state_file_path):
                optics_debug(f'creating {state_file_path}')
                utils.add_last_line(state_file_path, TEST_HISTORY_FIRST_LINE_PREFIX + scene_name)          
                init_state = utils.get_session_message(NOT_ATTEMPTED)
                utils.add_last_line(state_file_path, init_state)

    def has_more_scenes_to_run(self, path_list, types_to_skip):
        optics_debug('has more scenes to run?')
        state_dir = self.systest_dirs.scene_state_dir
        for path in path_list:
            state_path = utils.get_state_path_for_scene_path(path, state_dir)
            scene_type = utils.get_scene_type_for_state_path(state_path)
            #optics_debug(f'checking {state_path}')
            #optics_debug(f'deduced scene type {scene_type}')
            if scene_type in types_to_skip:
                optics_debug(f'found scene type {scene_type} in types_to_skip: {types_to_skip}')
            else:
                #optics_debug(f'not supposed to skip {scene_type}')
                if self.is_awaiting_assignment(state_path):
                    optics_debug(f'{state_path} was awaiting assignment ... returning True')
                    return True
        optics_info('found no more scenes to run... return False')
        return False

    def has_more_smoke_test_scenes_to_run(self, path_list, types_to_skip):
        state_dir = self.systest_dirs.scene_state_dir
        smoke_path_list = utils.filter_pathnames_for_smoke_test(path_list)
        for path in smoke_path_list:
            state_path = utils.get_state_path_for_scene_path(path, state_dir)
            scene_type = utils.get_scene_type_for_state_path(state_path)
            if not scene_type in types_to_skip:
                if self.is_awaiting_assignment(state_path):
                    return True
        return False

    def assign_next_scene(self, scene_path_list, types_to_skip):
        optics_debug(f'assigning next scene from scene_path_list of length {len(scene_path_list)}')
        optics_debug(f'abiding types to skip: {types_to_skip}')
        state_dir = self.systest_dirs.scene_state_dir
        for scene_path in scene_path_list:
            state_path = utils.get_state_path_for_scene_path(scene_path, state_dir)
            scene_type = utils.get_scene_type_for_state_path(state_path)
            if not scene_type in types_to_skip:
                scene_name = os.path.basename(scene_path).split('.')[0]
                if self.is_awaiting_assignment(state_path):
                    self.note_assignment(state_path)
                    optics_debug(f'{scene_name} ASSIGNED')
                    return scene_path
                else:
                    optics_debug(f'{scene_name} already assigned')
        optics_debug('returning NO MORE SCENES TO RUN from assign_next_scene()')
        return NO_MORE_SCENES_TO_RUN


    def assign_next_smoke_test_scene(self, scene_path_list, types_to_skip):
        state_dir = self.systest_dirs.scene_state_dir
        smoke_path_list = utils.filter_pathnames_for_smoke_test(scene_path_list)
        for smoke_path in smoke_path_list:
            print(f'[tman]...smoke path: {smoke_path}')
        for scene_path in smoke_path_list:
            state_path = utils.get_state_path_for_scene_path(scene_path, state_dir)
            scene_type = utils.get_scene_type_for_state_path(state_path)
            if not scene_type in types_to_skip:
                if self.is_awaiting_assignment(state_path):
                    print(f'[tman]...assigning smoke test scene: {scene_path}')
                    self.note_assignment(state_path)
                    return scene_path
                else:
                    scene_name = os.path.basename(scene_path).split('.')[0]
                    #print(f'[tman]...{scene_name} already assigned')
        return NO_MORE_SCENES_TO_RUN

    def note_assignment(self, state_path):
        utils.add_last_line(state_path, utils.get_register_status_message(IN_PROGRESS_SCENE_ASSIGNED))

        
    def is_awaiting_assignment(self, state_path):
        optics_debug(f'is awaiting assignment?: {state_path}')
        if not os.path.exists(state_path):
            optics_error(f'state_path does not exist: {state_path}')
            return False
        line = utils.get_last_line(state_path)
        run_state = utils.parse_run_state(line)
        optics_debug(f'encountered run_state {run_state}')
        opics_run_state = OpicsRunState('pretend/scene/path')
        return opics_run_state.should_tman_assign_scene_in_state(run_state)

    ##########################################################################
    # api used by tstat.py
    ##########################################################################
   
    def show_session_status(self):
        session_files = os.listdir(self.systest_dirs.sessions_dir)
        
        print(utils.header(f' sessions: {len(session_files)}'))
        for session_file in session_files:
            try:
                session_path = os.path.join(self.systest_dirs.sessions_dir, session_file)
                f = open(session_path, 'r')
                lines = f.readlines()
                f.close()
                #print(f'session path {session_path}')
                trun_session = OpticsSession(lines)
                if trun_session.healthy:
                    trun_session.summary()
                else:
                    print(f'session not healthy: {session_path} {trun_session.state}')
            except Exception as e:
                print('ERROR -- problem with session file: ', session_file)

    def gather_do_types_from_spec(self, do_types_list):
        self.scenes_do_type = do_types_list
        return None



    def gather_scene_state_paths(self):
        result = []
        scene_state_dir = self.systest_dirs.scene_state_dir
        type_dirs = os.listdir(scene_state_dir)
        # print(f'...do_types_list: {self.scenes_do_type}')
        # print(f'...list of type dirs: {type_dirs}')
        for type_dir in type_dirs:
            if type_dir not in self.scenes_do_type:
                pass
            else:
                type_dir_path = os.path.join(scene_state_dir, type_dir)
                # print(f'...gathering scene state paths from {type_dir_path}')
                files = os.listdir(type_dir_path)
                # print(f'...found {len(files)} files')
                for file in files:
                    # print(f'...found file {file}')
                    path = os.path.join(type_dir_path, file)
                    # print(f'...path: {path}')
                    result.append(path)
        return result

 


    def load_scene_state_histories(self):
        scene_state_paths = self.gather_scene_state_paths()
        scene_state_paths.sort()
        scene_state_histories = []
        for scene_state_path in scene_state_paths:
            try:
                f = open(scene_state_path, 'r')
                lines = f.readlines()
                f.close()
                scene_name = os.path.basename(scene_state_path).split('.')[0]
                scene_state_history = SceneStateHistory(scene_name, lines)
                if scene_state_history.is_well_formatted:
                    scene_state_histories.append(scene_state_history)
                else:
                    print('')
                    print(f'...WARNING scene state history for {scene_name} is corrupted and is being ignored')
                    print('')
            except Exception as e:
                print(f'...ERROR -- Problem loading scene state history for {scene_name}')
        return scene_state_histories

    def show_runs_summary(self):
        scene_state_histories = self.load_scene_state_histories()
        print(utils.header(f' runs: {self.get_completed_scene_count(scene_state_histories)}/{len(scene_state_histories)}'))
        opics_run_state = OpicsRunState('')
        opics_run_state.show_runs_summary(scene_state_histories)

    def show_gpu_mem_fail_retry_count(self):
        scene_state_histories = self.load_scene_state_histories()
        print(utils.header(f' runs: {self.get_completed_scene_count(scene_state_histories)}/{len(scene_state_histories)}'))
        opics_run_state = OpicsRunState('')
        opics_run_state.show_gpu_mem_fail_retry_count(scene_state_histories)

    def show_scene_timings(self):
        scene_state_histories = self.load_scene_state_histories()
        print(utils.header(f' runs: {self.get_completed_scene_count(scene_state_histories)}/{len(scene_state_histories)}'))
        opics_run_state = OpicsRunState('')
        opics_run_state.show_scene_timings(scene_state_histories)

    def get_completed_scene_count(self,scene_state_histories):
        completed_count = 0
        for ssh in scene_state_histories:
            if ssh.is_completed():
                completed_count += 1
        return completed_count
    ##########################################################################
    # api used by forget_systest_data.py
    ##########################################################################

    def get_session_count(self):
        return len(os.listdir(self.systest_dirs.sessions_dir))

    def get_stdout_log_count(self):
        scene_types = os.listdir(self.systest_dirs.stdout_logs_dir)
        count = 0
        for scene_type in scene_types:
            count += len(os.listdir(os.path.join(self.systest_dirs.stdout_logs_dir, scene_type)))
        return count

    def get_mcs_log_count(self):
        scene_types = os.listdir(self.systest_dirs.result_logs_dir)
        count = 0
        for scene_type in scene_types:
            count += len(os.listdir(os.path.join(self.systest_dirs.result_logs_dir, scene_type)))
        return count

    def clean_systest_data(self,scene_type_choice):
        if scene_type_choice != 'all':
            scene_type_choice =   "".join(["/",scene_type_choice])       
        print(f'cleaning systest data...')        
        
        if scene_type_choice =='all':
            print('    forgetting sessions')
            os.system(f'rm -rf {self.systest_dirs.sessions_dir}/*')
            scene_type_choice = ''
        
        print(f'    forgetting {scene_type_choice} scene states')
        os.system(f'rm -rf {self.systest_dirs.scene_state_dir}{scene_type_choice}/*')
        print(f'    forgetting {scene_type_choice} mcs logs')
        os.system(f'rm -rf {self.systest_dirs.result_logs_dir}{scene_type_choice}/*')
        print(f'    forgetting {scene_type_choice} stdout logs')
        os.system(f'rm -rf {self.systest_dirs.stdout_logs_dir}{scene_type_choice}/*')
        print(f'    forgetting {scene_type_choice} videos')
        os.system(f'rm -rf {self.systest_dirs.videos_dir}/{scene_type_choice}/*')
        
class TestRegisterRemote():
    def __init__(self, systest_dirs):
        self.systest_dirs = systest_dirs
        self.has_requested_job = False
        
    ##########################################################################
    # api used by trun_system_tests.py, trun.py and SceneStatusUpdater
    ##########################################################################
    def derive_session_path(self, spec_name_sans_proj):
        t = int(time.time())
        machine = os.uname()[1]
        session_filename = f'runner_session_{spec_name_sans_proj}_{machine}_{t}.txt'
        self.session_path = os.path.join(self.systest_dirs.sessions_dir, session_filename)
        # optics_info(f'registering session {session_filename}')
        # utils.remote_copy_file(local_path, self.session_path)
        #utils.remote_add_last_line(self.session_path, session_start_string)


    def is_session_killed(self):
        optics_debug('is session killed? ')
        session_path = self.session_path
        last_line = utils.remote_get_last_line(session_path)
        optics_debug(f'last line read as : {last_line}')
        if 'SESSION_KILLED' in last_line:
            optics_debug('SESSION_KILLED determined as YES')
            return True
        optics_debug('SESSION_KILLED determined as NO')
        return False

 
    def set_session_path(self, session_path):
        # this is needed because run_optics_scene.py needs the session_path to be passed in as an argument by  optics_test_runner.py. 
        # i.e. optics_test_runner.py calls derive_session_path to set it initially, and then needs to pass that derived path in full the
        # run_optics_script that it calls 
        self.session_path = session_path


    def request_job(self, proj, run_mode):
        machine = os.uname()[1]
        if run_mode == SMOKE_TEST:
            request = JOB_REQUEST_SMOKE
        else:
            request = JOB_REQUEST
        job_request = utils.get_register_control_message(request, proj)
        optics_info(f'requesting job')
        if not self.has_requested_job:
            t = int(time.time())
            machine = os.uname()[1]
            session_start_string = f'# trun_session;{proj};{machine};{t}'
            utils.remote_add_last_line(self.session_path, session_start_string+'\n'+job_request)
            # utils.remote_add_last_line(self.session_path, job_request)
            self.has_requested_job = True
        else: 
            utils.remote_add_last_line(self.session_path, job_request)

        # utils.remote_add_last_line(self.session_path, job_request)
        scene_path = self.await_job_assign_from_tman(machine, self.session_path, 20, 5)
        return scene_path


    def await_job_assign_from_tman(self, requesting_machine, session_path, tries, sleep_time):
        optics_debug('awaiting job assing from manager')
        for i in range(tries):
            time.sleep(sleep_time)
            optics_debug('(checking for response job request)')
            last_line = utils.remote_get_last_line(session_path)
            if JOB_ASSIGN in last_line:
                designated_machine, _, scene_path = utils.parse_job_assign(last_line)
                optics_debug(f'job assign found for scene {scene_path}')
                #if designated_machine == requesting_machine:
                return scene_path
        optics_fatal(f'no response from tman on JOB_REQUEST - check to make sure tman.py is running')


    def note_scene_state(self, scene_path, state):
        state_dir = self.systest_dirs.scene_state_dir
        state_path = utils.get_state_path_for_scene_path(scene_path, state_dir)
        optics_debug(f'noting scene state {state} for scene {os.path.basename(scene_path)}')
        utils.remote_add_last_line(state_path, utils.get_register_status_message(state))
        if 'SESSION_FATAL' in state:
            optics_debug(f'SESSION_FATAL detected - noting that')
            self.note_session_fatal(scene_path)


    def note_session_fatal(self, scene_path):
        session_path = self.session_path
        utils.remote_add_last_line(session_path, utils.get_session_message(SESSION_KILLED))

    def store_scene_log(self, log_path):
        optics_info(f'storing scene log {log_path}')
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = get_abbrev_scene_type_from_filename(log_name)
        dest_log_path = os.path.join(self.systest_dirs.result_logs_dir, scene_type, log_file)
        optics_debug(f'remote path will be {dest_log_path}')
        utils.remote_ensure_dir_exists(os.path.dirname(dest_log_path))
        utils.remote_copy_file(log_path, dest_log_path)


    def store_stdout_log(self, log_path):
        optics_info(f'storing stdout log {log_path}')
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = get_abbrev_scene_type_from_filename(log_name)
        dest_log_path = os.path.join(self.systest_dirs.stdout_logs_dir, scene_type, log_file)
        optics_debug(f'remote path will be {dest_log_path}')
        utils.remote_ensure_dir_exists(os.path.dirname(dest_log_path))
        utils.remote_copy_file(log_path, dest_log_path)


    def store_videos(self, videos_dir_path):
        # videos_dir == scene_name
        optics_info(f'remotely storing videos {videos_dir_path}')
        videos_dir = os.path.basename(videos_dir_path)
        optics_info(f'videos_dir is {videos_dir}')
        scene_type = get_abbrev_scene_type_from_filename(videos_dir)
        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'topdown')
        optics_info(f'src:  {src}')
        optics_info(f'dest: {dest}')
        utils.remote_ensure_dir_exists(os.path.dirname(dest))
        utils.remote_copy_file(src, dest)
        optics_info('copied topdown')
        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'visual')
        utils.remote_copy_file(src, dest)
        optics_info('copied visual')
        # abstain from copying depth and segmentation videos as per Rajesh request
        # (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'depth')
        # utils.remote_copy_file(src, dest)

        # (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'segmentation')
        # utils.remote_copy_file(src, dest)


    def fetch_remote_file(self, remote_path, local_path):
        utils.remote_get_file(remote_path,local_path)
    ##########################################################################
    # api used by tstat.py
    ##########################################################################
    

