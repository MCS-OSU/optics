from pathlib import Path
import time
from core.optics_run_state     import OpticsRunState
from core.test_register        import TestRegisterLocal, TestRegisterRemote
from core.optics_dirs          import SystestDirectories
from core.utils                import ensure_dirs_exist, remote_ensure_dirs_exist, ensure_dir_exists
from core.constants            import NO_MORE_SCENES_TO_RUN
from core.constants            import EC2B_HOME
import self_test.optics_self_test_util as util
from scripts.opics_run_state   import FAILED_GPU_MEM_RETRY, FAILED_TIMEOUT

class OpticsSelfTestRunner():
    def __init__(self, optics_spec, manager_proximity, run_mode):
        self.run_mode = run_mode
        self.optics_spec = optics_spec
        if manager_proximity == 'local':  
            home_dir = str(Path.home())
            self.systest_dirs = SystestDirectories(home_dir, optics_spec)      
            print('...ensuring local directories exist')
            ensure_dirs_exist(self.systest_dirs.get_top_level_dirs())
            print('...local directories ensured')

        else:
            home_dir = EC2B_HOME
            self.systest_dirs = SystestDirectories(home_dir, optics_spec)
            print('...ensuring remote directories exist')
            remote_ensure_dirs_exist(self.systest_dirs.get_top_level_dirs())
            print('...remote directories ensured')

        
        if manager_proximity == 'local':
            # trun  will read and write files directly
            self.test_register = TestRegisterLocal(self.systest_dirs)
        else:
            # trun will transact files with ec2b via scp
            self.test_register = TestRegisterRemote(self.systest_dirs)
        self.test_register.register_session('self_test')



    def normal_healthy_state_progression(self):
        scene_path = self.test_register.request_job('self_test', self.run_mode)
        print(f'...tasked with {scene_path}...')
        time.sleep(2)
        run_state = OpticsRunState(scene_path)
        run_state.set_test_register(self.test_register)
        run_state.starting_scene()
        #test_register.note_starting_scene(     scene_path, machine, t)
        time.sleep(2)
        run_state.starting_controller()
        #test_register.note_starting_controller(scene_path, machine, t)
        time.sleep(2)
        run_state.scene_running()
        #test_register.note_scene_running(      scene_path, machine, t)
        time.sleep(2)
        run_state.scene_completed()
        #test_register.note_scene_completed(    scene_path, machine, t)

        log_dir = 'optics_selftest_logdir'
        ensure_dirs_exist([log_dir])
        print('ensured remote log dir exists')
        log_path = util.create_bogus_logfile(log_dir, scene_path, self.optics_spec.proj, scene_correct=True)
        print(f'bogus log path is {log_path}')
        self.test_register.store_scene_log(log_path)
        print('stored log')


    def test_gpu_mem_failure(self):
        run_state = OpticsRunState('')
        try:
            s = 'line1\nline2\nCUDA out of memory\nline4'
            raise Exception(s)
        except Exception as e:
            run_state.convert_exception_to_run_state(e,'selt test')
            assert run_state.state == FAILED_GPU_MEM_RETRY
            print('[optics]...test_gpu_mem_failure passed')

    def test_timeout_failure(self):
        run_state = OpticsRunState('')
        try:
            s = 'line1\nline2\nController instantiation Time out condition \nline4'
            raise Exception(s)
        except Exception as e:
            run_state.convert_exception_to_run_state(e,'selt test')
            assert run_state.state == FAILED_TIMEOUT
            print('[optics]...test_timeout_failure passed')