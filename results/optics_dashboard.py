from pathlib import Path

from core.constants          import EC2_MACHINE_HOME
from core.optics_dirs        import SystestDirectories
from core.test_register      import TestRegisterLocal, TestRegisterRemote


class OpticsDashboard():
    def __init__(self, manager_proximity, optics_spec):
        if manager_proximity == 'local':
            home_dir = str(Path.home())
            systest_dirs = SystestDirectories(home_dir, optics_spec)     
            self.test_register = TestRegisterLocal(systest_dirs)
        else:
            home_dir = EC2_MACHINE_HOME
            systest_dirs = SystestDirectories(home_dir, optics_spec)
            self.test_register = TestRegisterRemote(systest_dirs) 

    def show_all(self):
        self.test_register.show_session_status()
        self.test_register.show_runs_summary()
        self.test_register.show_gpu_mem_fail_retry_count()
        self.test_register.show_scene_timings()
    