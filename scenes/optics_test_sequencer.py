from pathlib import Path
import time
from datetime import datetime
import os
from core.optics_dirs        import SystestDirectories
from core.test_register      import TestRegisterLocal
from core.runner_sessions    import RunnerSessions
from core.utils              import get_last_line, add_last_line, get_register_control_message, parse_job_request, ensure_dirs_exist
from core.constants          import JOB_ASSIGN, JOB_REQUEST, JOB_REQUEST_SMOKE, NO_MORE_SCENES_TO_RUN
from scenes.optics_test_sets import OpticsTestSets
from core.utils              import optics_info, optics_error, optics_debug

class OpticsTestSequencer():
    def __init__(self, optics_spec):
        self.optics_spec = optics_spec
        optics_info('initializing OpticsTestSequencer')
        home_dir = str(Path.home())
        self.systest_dirs = SystestDirectories(home_dir, optics_spec)
        top_level_dirs = self.systest_dirs.get_top_level_dirs()
        ensure_dirs_exist(top_level_dirs)

        self.test_register = TestRegisterLocal(self.systest_dirs)
        self.optics_test_sets = OpticsTestSets(optics_spec, self.systest_dirs)
        self.scene_path_list = self.optics_test_sets.get_all_paths()
        self.test_register.init_scene_state_files(self.scene_path_list)
        self.runner_sessions = RunnerSessions(self.systest_dirs.sessions_dir)


    def start(self):
        while True:
            #print('...scanning for job requests')
            self.answer_job_requests()
            time.sleep(3)

 
    def answer_job_requests(self):
        sessions = self.runner_sessions.get_sessions_with_job_requests()
        optics_debug(f'sessions with job_requests {len(sessions)}')
        for session in sessions:
            optics_debug(f'checking {session}')
            potential_job_request = get_last_line(session)
            if potential_job_request.startswith('#'):
                optics_debug('job request scanner encountered comment line - skipping this pass...')
                continue
            machine,command = parse_job_request(potential_job_request)
            optics_debug(f' machine: {machine} command: {command}')
            types_to_skip = self.optics_spec.types_to_skip
            if command == JOB_REQUEST:
                optics_debug(f'job request from {machine}')
                next_scene_path = self.test_register.assign_next_scene(self.scene_path_list, types_to_skip)
                if NO_MORE_SCENES_TO_RUN == next_scene_path:
                    add_last_line(session, get_register_control_message(NO_MORE_SCENES_TO_RUN, '---'))
                    optics_info('NO MORE SCENES TO RUN...')
                else:
                    next_scene_name = os.path.basename(next_scene_path)
                    timestamp = datetime.today().strftime("%d-%H:%M:%S")
                    optics_info(f'{timestamp} - {next_scene_name}   assigned to   {machine}')
                    add_last_line(session, get_register_control_message(JOB_ASSIGN, next_scene_path))                    
            else:
                optics_error(f'unknown command {command} in {session}')


    def answer_job_requests_orig(self):
        sessions = self.runner_sessions.get_sessions_with_job_requests()
        optics_debug(f'sessions with job_requests {len(sessions)}')
        for session in sessions:
            optics_info(f'checking {session}')
            potential_job_request = get_last_line(session)
            if potential_job_request.startswith('#'):
                optics_debug('job request scanner encountered comment line - skipping this pass...')
                continue
            machine,command = parse_job_request(potential_job_request)
            optics_info(f' machine: {machine} command: {command}')
            types_to_skip = self.optics_spec.types_to_skip
            if command == JOB_REQUEST:
                optics_info(f'job request from {machine} for {self.optics_spec.name}')
                if self.test_register.has_more_scenes_to_run(self.scene_path_list, types_to_skip):
                    optics_info(f'HAS MORE SCENES TO RUN')
                    next_scene_path = self.test_register.assign_next_scene(self.scene_path_list, types_to_skip)
                    optics_info(f'assigned {next_scene_path}')
                    add_last_line(session, get_register_control_message(JOB_ASSIGN, next_scene_path))
                else:
                    add_last_line(session, get_register_control_message(NO_MORE_SCENES_TO_RUN, '---'))
                    optics_info('NO MORE SCENES TO RUN...')
            elif command == JOB_REQUEST_SMOKE:
                if self.test_register.has_more_smoke_test_scenes_to_run(self.scene_path_list, types_to_skip):
                    optics_info(f'job request from {machine} for {self.optics_spec.name}')
                    next_scene_path = self.test_register.assign_next_smoke_test_scene(self.scene_path_list, types_to_skip)
                    optics_info(f'assigned {next_scene_path}')
                    add_last_line(session, get_register_control_message(JOB_ASSIGN, next_scene_path))
                else:
                    add_last_line(session, get_register_control_message(NO_MORE_SCENES_TO_RUN, '---'))
                    optics_info('NO MORE SCENES TO RUN...')
            else:
                optics_error(f'unknown command {command} in {session}')