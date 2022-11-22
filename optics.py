import sys, os
#import sh
import subprocess
from core.constants                    import EC2B_UNAME_OUTPUT, TEST_SET_ORDER, SMOKE_TEST
from scenes.optics_test_sequencer      import OpticsTestSequencer
from core.optics_test_runner           import OpticsTestRunner
from self_test.optics_self_test_runner import OpticsSelfTestRunner
from core.optics_spec_loader           import OpticsSpec
from admin.optics_stopper              import OpticsStopper
from admin.optics_results_eraser       import OpticsResultsEraser
from results.optics_dashboard          import OpticsDashboard
from env.env_snapshot                  import EnvSnapshot

def verify_conda_env_for_project_is_activated(proj):
    if 'CONDA_DEFAULT_ENV' not in os.environ:
        exit_with(f'ERROR: CONDA_DEFAULT_ENV not set - do "conda activate env_{proj}')
    if os.environ['CONDA_DEFAULT_ENV'] != f'env_{proj}':
        exit_with(f'ERROR: CONDA_DEFAULT_ENV does not match {proj} - should be env_{proj}')

def is_running_on_ec2b():
    return os.uname()[1] == EC2B_UNAME_OUTPUT

def is_optics_manager_running_locally(spec_path):
    #result = sh.grep(sh.grep(sh.grep(sh.ps('edalf'),'optics'),'manager'), spec_name)
    ps = subprocess.Popen(('ps', '-edalf'), stdout=subprocess.PIPE)
    result = ps.communicate()[0].decode('utf-8')
    for line in result.splitlines():
        if 'optics' in line and 'manager' in line and spec_path in line:
            print(f'found optics manager running locally for {spec_path}')
            return True
    print(f'no optics manager running locally for {spec_path}')
    return False

def get_manager_proximity(spec_path):
    if is_optics_manager_running_locally(spec_path):
        return 'local'
    else:
        if is_running_on_ec2b():
            return 'local'
        return 'remote'

def exit_with(msg):
    print(msg)
    sys.exit()

def usage():
    print("python optics.py manager|smoke_test|run_scenes|stop|erase_results|status|env_snapshot <optics_config>")
    print('        manager - will only work when incoked on ec2b')
    print('        run_scene - will run a scene form any machine if the env is deemed to match the one specified in the config')


if __name__ == '__main__':
    
    if not 'OPICS_HOME' in os.environ:
        exit_with('ERROR - OPICS_HOME not defined.  Please "export OPICS_HOME=<parent_of_opics_dir>"')
        
    if len(sys.argv) < 3:
        usage()
        sys.exit()

    if sys.argv[1] not in ['manager','smoke_test', 'run_scenes','stop','erase_results','status','env_snapshot']:
        usage()
        sys.exit()

    cmd = sys.argv[1]
    optics_spec_path = sys.argv[2]
    optics_spec = OpticsSpec(optics_spec_path)

    proj            = optics_spec.proj
    version         = optics_spec.version
    controller_type = optics_spec.controller
    spec_name       = optics_spec.name
    
    if not cmd == 'manager':
        manager_proximity = get_manager_proximity(optics_spec_path)
        print(f'manager_proximity: {manager_proximity}')


    if cmd == 'manager':
        if version != 'self_test':
            if not is_running_on_ec2b():
                print('ERROR - manager command can only be invoked on ec2b')
                sys.exit()
        print('...running manager...')
        ots = OpticsTestSequencer(optics_spec)
        ots.start()

    elif cmd == 'run_scenes':
        verify_conda_env_for_project_is_activated(proj)
        print('...running scenes...')
        if version == 'self_test':
            if not is_optics_manager_running_locally(optics_spec_path):
                answer = input('no manager running locally - are you self-testing remote?')
                if answer != 'y':
                    print('exiting')
                    sys.exit()
            print('...running self_test')
            otsr = OpticsSelfTestRunner(optics_spec, manager_proximity)
            otsr.normal_healthy_state_progression()
            otsr.test_gpu_mem_failure()
            otsr.test_timeout_failure()
        else:
            otr = OpticsTestRunner(optics_spec_path, manager_proximity, TEST_SET_ORDER)
            otr.run()
    elif cmd == 'smoke_test':
            otr = OpticsTestRunner(optics_spec_path, manager_proximity, SMOKE_TEST)
            otr.run()

    elif cmd == 'stop':
        stopper = OpticsStopper(optics_spec)
        stopper.stop_processes()
        sys.exit()

    elif cmd == 'erase_results':
        if not is_running_on_ec2b():
            print('ERROR - erase_results command can only be invoked on ec2b')
            sys.exit()
        manager_process = os.popen(f'ps -edalf | grep -v edalf | grep optics | grep {optics_spec}').read()
        if manager_process:
            print(f'[optics]...ERROR: optics manager is running for {optics_spec_path} - stop it and try again')
            print(f'[optics]...manager_process {manager_process}')
            sys.exit()
        else:
            optics_results_eraser = OpticsResultsEraser(optics_spec)
            optics_results_eraser.erase_results()
            sys.exit()

    elif cmd == 'status':
        dashboard = OpticsDashboard(manager_proximity, optics_spec)
        dashboard.show_all()

    elif cmd == 'env_snapshot':
        verify_conda_env_for_project_is_activated(proj)
        ss = EnvSnapshot(optics_spec_path)
        sys.exit()

    else:
        usage()
        sys.exit()