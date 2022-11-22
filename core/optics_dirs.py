import os
from pathlib import Path


class SystestDirectories():
    def __init__(self, home_dir, optics_spec):
        proj = optics_spec.proj
        version = optics_spec.version

        self.systest_dir = os.path.join(home_dir, 'eval6_systest')
        # populated prior to test run
        self.priorities_dir    = os.path.join(self.systest_dir, proj, 'priorities')
        self.test_sets         = os.path.join(self.systest_dir, proj, 'test_sets')

        # populated by the test run
        self.result_logs_dir   = os.path.join(self.systest_dir, proj, 'versions', version, 'logs')
        self.stdout_logs_dir   = os.path.join(self.systest_dir, proj, 'versions', version, 'stdout_logs')
        self.sessions_dir      = os.path.join(self.systest_dir, proj, 'versions', version, 'sessions')
        self.scene_state_dir   = os.path.join(self.systest_dir, proj, 'versions', version, 'scene_state')
        self.eval5_answer_keys_dir = os.path.join(self.systest_dir, 'answer_keys', proj)
        print('optics dirs:')
        print(f' - systest_dir:      {self.systest_dir}')
        print(f' - result_logs_dir:  {self.result_logs_dir}')
        print(f' - stdout_logs_dir:  {self.stdout_logs_dir}')
        print(f' - sessions_dir:     {self.sessions_dir}')

    
    def get_top_level_dirs(self):
        dirs = []
        dirs.append(self.systest_dir)
        dirs.append(self.result_logs_dir)
        dirs.append(self.stdout_logs_dir)
        dirs.append(self.sessions_dir)
        dirs.append(self.scene_state_dir)
        return dirs


    