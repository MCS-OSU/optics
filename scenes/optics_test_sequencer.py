from pathlib import Path
import time
import os
from core.optics_dirs        import SystestDirectories
from core.test_register      import TestRegisterLocal
from core.runner_sessions    import RunnerSessions
from core.utils              import get_last_line, add_last_line, get_register_control_message, parse_job_request, ensure_dirs_exist
from core.constants          import JOB_ASSIGN, JOB_REQUEST, JOB_REQUEST_SMOKE, NO_MORE_SCENES_TO_RUN
from scenes.optics_test_sets import OpticsTestSets

class OpticsTestSequencer():
    def __init__(self, optics_spec):
        self.optics_spec = optics_spec
        print('...initializing OpticsTestSequencer')
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
        for session in sessions:
            print(f'checking {session}')
            potential_job_request = get_last_line(session)
            machine,command = parse_job_request(potential_job_request)
            print(f' machine: {machine} command: {command}')
            types_to_skip = self.optics_spec.types_to_skip
            if command == JOB_REQUEST:
                if self.test_register.has_more_scenes_to_run(self.scene_path_list, types_to_skip):
                    print(f'job request from {machine} for {self.optics_spec.name}')
                    next_scene_path = self.test_register.assign_next_scene(self.scene_path_list, types_to_skip)
                    print(f'assigned {next_scene_path}')
                    add_last_line(session, get_register_control_message(JOB_ASSIGN, next_scene_path))
                else:
                    add_last_line(session, get_register_control_message(NO_MORE_SCENES_TO_RUN, '---'))
            elif command == JOB_REQUEST_SMOKE:
                if self.test_register.has_more_smoke_test_scenes_to_run(self.scene_path_list, types_to_skip):
                    print(f'job request from {machine} for {self.optics_spec.name}')
                    next_scene_path = self.test_register.assign_next_smoke_test_scene(self.scene_path_list, types_to_skip)
                    print(f'assigned {next_scene_path}')
                    add_last_line(session, get_register_control_message(JOB_ASSIGN, next_scene_path))
                else:
                    add_last_line(session, get_register_control_message(NO_MORE_SCENES_TO_RUN, '---'))
            else:
                print(f'unknown command {command} in {session}')