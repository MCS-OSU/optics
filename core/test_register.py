from importlib.util import set_loader
import os, time, sys
import core.utils as utils
import opics.common.logging.log_constants as log_constants
from scripts.opics_run_state        import NOT_ATTEMPTED, IN_PROGRESS_SCENE_ASSIGNED, OpicsRunState
from core.constants                 import JOB_REQUEST, JOB_REQUEST_SMOKE, JOB_ASSIGN, NO_MORE_SCENES_TO_RUN, SESSION_KILLED, SMOKE_TEST
from core.optics_session            import OpticsSession
from results.scene_state_history    import SceneStateHistory



class TestRegisterLocal():
    def __init__(self, systest_dirs):
        self.systest_dirs = systest_dirs

    ##########################################################################
    # api used by OpticsTestRunner and OpicsRunState
    ##########################################################################
    def register_session(self, proj):
        t = int(time.time())
        machine = os.uname()[1]
        session_start_string = f'# trun_session;{proj};{machine};{t}'
        session_filename = f'runner_session_{proj}_{machine}_{t}.txt'
        self.session_path = os.path.join(self.systest_dirs.sessions_dir, session_filename)
        print(f'[optics]...registering session')
        utils.add_last_line(self.session_path, session_start_string)

    def is_session_killed(self):
        session_path = self.session_path
        last_line = utils.get_last_line(session_path)
        if 'SESSION_KILLED' in last_line:
            return True
        return False

    def set_session_path(self, session_path):
        # this is needed because trun.py creates the session.  For systest_run_opics_scene to tweak that session file, 
        # it needs to know where it is.
        self.session_path = session_path

    def request_job(self, proj, run_mode):
        machine = os.uname()[1]
        if run_mode == SMOKE_TEST:
            request = JOB_REQUEST_SMOKE
        else:
            request = JOB_REQUEST
        job_request = utils.get_register_control_message(request, proj)
        print(f'[optics]...requesting job')
        utils.add_last_line(self.session_path, job_request)
        scene_path = self.await_job_assign_from_tman(machine, self.session_path, 3, 1.5)
        print(f'[optics]...got job: {scene_path}')
        return scene_path


    def await_job_assign_from_tman(self, requesting_machine, session_path, tries, sleep_time):
        for i in range(tries):
            time.sleep(sleep_time)
            print('(checking for response job request)')
            last_line = utils.get_last_line(session_path)
            if NO_MORE_SCENES_TO_RUN in last_line:
                return NO_MORE_SCENES_TO_RUN
            if JOB_ASSIGN in last_line:
                designated_machine, _, scene_path = utils.parse_job_assign(last_line)
                if designated_machine == requesting_machine:
                    return scene_path
        print(f'[optics]...no response from tman on JOB_REQUEST')
        print('[optics]...Check to make sure tman.py is running.')
        sys.exit(1)


    def note_scene_state(self, scene_path, state):
        state_dir = self.systest_dirs.scene_state_dir
        print(f'[optics]...{state}')
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
        scene_type = log_constants.get_abbrev_scene_type_from_filename(log_name)
        dest_path = os.path.join(self.systest_dirs.result_logs_dir, scene_type, log_file)
        print(f'...storing mcs log')
        utils.ensure_dir_exists(os.path.dirname(dest_path))
        os.system(f' cp {log_path} {dest_path}')


    def store_stdout_log(self, log_path):
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = log_constants.get_abbrev_scene_type_from_filename(log_name)
        dest_path = os.path.join(self.systest_dirs.stdout_logs_dir, scene_type, log_file)
        print(f'[optics]...storing stdout log')
        utils.ensure_dir_exists(os.path.dirname(dest_path))
        os.system(f' cp {log_path} {dest_path}')



    def store_videos(self, videos_dir):
        # videos_dir == scene_name
        scene_type = log_constants.get_abbrev_scene_type_from_filename(videos_dir)
        (src, dest) = utils.get_pathnames_for_video(videos_dir, scene_type, self.systest_dirs.videos_dir, 'depth')
        utils.ensure_dir_exists(os.path.dirname(dest))
        os.system(f' cp {src} {dest}')

        (src, dest) = utils.get_pathnames_for_video(videos_dir, scene_type, self.systest_dirs.videos_dir, 'segmentation')
        os.system(f' cp {src} {dest}')

        (src, dest) = utils.get_pathnames_for_video(videos_dir, scene_type, self.systest_dirs.videos_dir, 'topdown')
        os.system(f' cp {src} {dest}')

        (src, dest) = utils.get_pathnames_for_video(videos_dir, scene_type, self.systest_dirs.videos_dir, 'visual')
        os.system(f' cp {src} {dest}')


    ##########################################################################
    # api used by manager
    ##########################################################################

    def init_scene_state_files(self, scene_paths):
        for scene_path in scene_paths:
            #print(f'path: {path}')
            scene_fname = os.path.basename(scene_path)
            scene_name = scene_fname.split('.')[0]
            #state_file_path  = os.path.join(self.systest_dirs.scene_state_dir, scene_name + '_state.txt')
            state_file_path = utils.get_state_path_for_scene_path(scene_path, self.systest_dirs.scene_state_dir)
            utils.ensure_dir_exists(os.path.dirname(state_file_path))
            if not os.path.exists(state_file_path):
                utils.add_last_line(state_file_path,'# test history for scene: ' + scene_name)          
                init_state = utils.get_session_message(NOT_ATTEMPTED)
                utils.add_last_line(state_file_path, init_state)

    def has_more_scenes_to_run(self, path_list, types_to_skip):
        state_dir = self.systest_dirs.scene_state_dir
        for path in path_list:
            state_path = utils.get_state_path_for_scene_path(path, state_dir)
            scene_type = utils.get_scene_type_for_state_path(state_path)
            if not scene_type in types_to_skip:
                if self.is_awaiting_assignment(state_path):
                    return True
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
        state_dir = self.systest_dirs.scene_state_dir
        for scene_path in scene_path_list:
            state_path = utils.get_state_path_for_scene_path(scene_path, state_dir)
            scene_type = utils.get_scene_type_for_state_path(state_path)
            if not scene_type in types_to_skip:
                if self.is_awaiting_assignment(state_path):
                    self.note_assignment(state_path)
                    return scene_path
                else:
                    scene_name = os.path.basename(scene_path).split('.')[0]
                    #print(f'[tman]...{scene_name} already assigned')
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
        if not os.path.exists(state_path):
            return False
        line = utils.get_last_line(state_path)
        run_state = utils.parse_run_state(line)
        opics_run_state = OpicsRunState('pretend/scene/path')
        return opics_run_state.should_tman_assign_scene_in_state(run_state)

    ##########################################################################
    # api used by tstat.py
    ##########################################################################
   
    def show_session_status(self):
        session_files = os.listdir(self.systest_dirs.sessions_dir)
        
        print(utils.header(f' sessions: {len(session_files)}'))
        for session_file in session_files:
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

    def gather_scene_state_paths(self):
        result = []
        scene_state_dir = self.systest_dirs.scene_state_dir
        type_dirs = os.listdir(scene_state_dir)
        for type_dir in type_dirs:
            type_dir_path = os.path.join(scene_state_dir, type_dir)
            files = os.listdir(type_dir_path)
            for file in files:
                path = os.path.join(type_dir_path, file)
                result.append(path)
        return result

    def load_scene_state_histories(self):
        scene_state_paths = self.gather_scene_state_paths()
        scene_state_paths.sort()
        scene_state_histories = []
        print(utils.header(f' runs: {len(scene_state_paths)}'))
        for scene_state_path in scene_state_paths:
            f = open(scene_state_path, 'r')
            lines = f.readlines()
            f.close()
            scene_name = os.path.basename(scene_state_path).split('.')[0]
            scene_state_history = SceneStateHistory(scene_name, lines)
            scene_state_histories.append(scene_state_history)
        return scene_state_histories

    def show_runs_summary(self):
        scene_state_histories = self.load_scene_state_histories()
        opics_run_state = OpicsRunState('')
        opics_run_state.show_runs_summary(scene_state_histories)

    def show_gpu_mem_fail_retry_count(self):
        scene_state_histories = self.load_scene_state_histories()
        opics_run_state = OpicsRunState('')
        opics_run_state.show_gpu_mem_fail_retry_count(scene_state_histories)

    def show_scene_timings(self):
        scene_state_histories = self.load_scene_state_histories()
        opics_run_state = OpicsRunState('')
        opics_run_state.show_scene_timings(scene_state_histories)

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

    def clean_systest_data(self):
        print(f'cleaning systest data...')
        print('    forgetting sessions')
        os.system(f'rm -rf {self.systest_dirs.sessions_dir}/*')
        print('    forgetting scene states')
        os.system(f'rm -rf {self.systest_dirs.scene_state_dir}/*')
        print('    forgetting mcs logs')
        os.system(f'rm -rf {self.systest_dirs.result_logs_dir}/*')
        print('    forgetting stdout logs')
        os.system(f'rm -rf {self.systest_dirs.stdout_logs_dir}/*')
        print('    forgetting videos')
        os.system(f'rm -rf {self.systest_dirs.videos_dir}/*')

class TestRegisterRemote():
    def __init__(self, systest_dirs):
        self.systest_dirs = systest_dirs
        
    ##########################################################################
    # api used by trun_system_tests.py, trun.py and SceneStatusUpdater
    ##########################################################################
    def register_session(self, proj):
        t = int(time.time())
        machine = os.uname()[1]
        session_start_string = f'# trun_session;{proj};{machine};{t}'
        session_filename = f'runner_session_{proj}_{machine}_{t}.txt'
        self.session_path = os.path.join(self.systest_dirs.sessions_dir, session_filename)
        print(f'[optics]...registering session')
        utils.remote_add_last_line(self.session_path, session_start_string)


    def is_session_killed(self):
        session_path = self.session_path
        last_line = utils.remote_get_last_line(session_path)
        if 'SESSION_KILLED' in last_line:
            return True
        return False

        
    def set_session_path(self, session_path):
        # this is needed because trun.py creates the session.  For systest_run_opics_scene to tweak that session file, 
        # it needs to know where it is.
        self.session_path = session_path


    def request_job(self, proj, run_mode):
        machine = os.uname()[1]
        if run_mode == SMOKE_TEST:
            request = JOB_REQUEST_SMOKE
        else:
            request = JOB_REQUEST
        job_request = utils.get_register_control_message(request, proj)
        print(f'[optics]...requesting job')
        utils.remote_add_last_line(self.session_path, job_request)
        scene_path = self.await_job_assign_from_tman(machine, self.session_path, 3, 4)
        return scene_path


    def await_job_assign_from_tman(self, requesting_machine, session_path, tries, sleep_time):
        for i in range(tries):
            time.sleep(sleep_time)
            #print('(checking for response job request)')
            last_line = utils.remote_get_last_line(session_path)
            if JOB_ASSIGN in last_line:
                designated_machine, _, scene_path = utils.parse_job_assign(last_line)
                #if designated_machine == requesting_machine:
                return scene_path
        print(f'[optics]...no response from tman on JOB_REQUEST - check to make sure tman.py is running')
        sys.exit(1)


    def note_scene_state(self, scene_path, state):
        state_dir = self.systest_dirs.scene_state_dir
        state_path = utils.get_state_path_for_scene_path(scene_path, state_dir)
        utils.remote_add_last_line(state_path, utils.get_register_status_message(state))
        if 'SESSION_FATAL' in state:
            self.note_session_fatal(scene_path)


    def note_session_fatal(self, scene_path):
        session_path = self.session_path
        utils.remote_add_last_line(session_path, utils.get_session_message(SESSION_KILLED))

    def store_scene_log(self, log_path):
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = log_constants.get_abbrev_scene_type_from_filename(log_name)
        dest_log_path = os.path.join(self.systest_dirs.result_logs_dir, scene_type, log_file)
        utils.remote_ensure_dir_exists(os.path.dirname(dest_log_path))
        utils.remote_copy_file(log_path, dest_log_path)


    def store_stdout_log(self, log_path):
        log_file = os.path.basename(log_path)
        log_name = log_file.split('.')[0]
        scene_type = log_constants.get_abbrev_scene_type_from_filename(log_name)
        dest_log_path = os.path.join(self.systest_dirs.stdout_logs_dir, scene_type, log_file)
        print(f'[optics]...storing log')
        utils.remote_ensure_dir_exists(os.path.dirname(dest_log_path))
        utils.remote_copy_file(log_path, dest_log_path)


    def store_videos(self, videos_dir_path):
        # videos_dir == scene_name
        videos_dir = os.path.basename(videos_dir_path)
        scene_type = log_constants.get_abbrev_scene_type_from_filename(videos_dir)
        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'depth')
        utils.remote_ensure_dir_exists(os.path.dirname(dest))
        utils.remote_copy_file(src, dest)

        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'segmentation')
        utils.remote_copy_file(src, dest)

        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'topdown')
        utils.remote_copy_file(src, dest)

        (src, dest) = utils.get_pathnames_for_video(videos_dir_path, scene_type, self.systest_dirs.videos_dir, 'visual')
        utils.remote_copy_file(src, dest)


    def fetch_remote_file(self, remote_path, local_path):
        utils.remote_get_file(remote_path,local_path)
    ##########################################################################
    # api used by tstat.py
    ##########################################################################
    

