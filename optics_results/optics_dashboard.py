from pathlib import Path
import sys
from core.constants          import EC2_MACHINE_HOME
from core.optics_dirs        import SystestDirectories
from core.optics_spec_loader import OpticsSpec
from core.test_register      import TestRegisterLocal, TestRegisterRemote
from optics_results.optics_sessions import OpticsSessions



def resolve_given_optics_spec_path(given_path):
    if given_path.startswith('/'):
        return given_path
    return os.path.join(os.getcwd(), given_path)

class OpticsDashboard():
    def __init__(self, manager_proximity, optics_spec):
        systest_dirs = None
        if manager_proximity == 'local':
            home_dir = str(Path.home())
            systest_dirs = SystestDirectories(home_dir, optics_spec)     
            self.test_register = TestRegisterLocal(systest_dirs)
        else:
            home_dir = EC2_MACHINE_HOME
            systest_dirs = SystestDirectories(home_dir, optics_spec)
            self.test_register = TestRegisterRemote(systest_dirs) 

        self.sessions = OpticsSessions(systest_dirs)


    def show_all(self):
        self.test_register.show_session_status()
        self.test_register.show_runs_summary()
        self.test_register.show_gpu_mem_fail_retry_count()
        self.test_register.show_scene_timings()
    


if __name__ == '__main__':
    prox = sys.argv[1]
    spec = sys.argv[2]
    optics_spec_path = resolve_given_optics_spec_path(spec)
    print(f'optics_spec_path: {optics_spec_path}')
    optics_spec = OpticsSpec(optics_spec_path)
    
    od = OpticsDashboard(prox, optics_spec)
    od.sessions.print_machine_names()
    print('sorting')
    od.sessions.sort_by_idle_time()
    od.sessions.print_machine_names()