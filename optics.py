import sys, os
#import sh
import subprocess
import logging
import time
from core.constants                    import TEST_SET_ORDER
from scenes.optics_test_sequencer      import OpticsTestSequencer
from core.optics_test_runner           import OpticsTestRunner
from self_test.optics_self_test_runner import OpticsSelfTestRunner
from core.optics_spec_loader           import OpticsSpec
from admin.optics_stopper              import OpticsStopper
from admin.optics_results_eraser       import OpticsResultsEraser
from optics_results.optics_dashboard   import OpticsDashboard
from optics_results.error_details      import ErrorDetails
from env.env_snapshot                  import EnvSnapshot
from core.utils                        import optics_fatal, optics_info, get_optics_datastore_proximity, is_running_on_ec2
from optics_results.optics_scores      import OpticsScores

def resolve_given_optics_spec_path(given_path):
    if given_path.startswith('/'):
        return given_path
    return os.path.join(os.getcwd(), given_path)
    
def verify_conda_env_for_project_is_activated(proj):
    if not proj in os.environ['CONDA_DEFAULT_ENV'] :
        optics_fatal(f'ERROR: {proj} not in CONDA_DEFAULT_ENV - be sure to activate the env first')

def is_optics_manager_running_locally(spec_path):
    print(f'checking if optics manager running locally for {spec_path}')
    #result = sh.grep(sh.grep(sh.grep(sh.ps('edalf'),'optics'),'manager'), spec_name)
    ps = subprocess.Popen(('ps', '-edalf'), stdout=subprocess.PIPE)
    result = ps.communicate()[0].decode('utf-8')
    for line in result.splitlines():
        #print(f'found line : {line}')
        if 'optics' in line and ' manager ' in line and spec_path in line:
            print(f'found optics manager running locally for {spec_path}')
            return True
    print(f'no optics manager running locally for {spec_path}')
    return False

def is_already_manager_running_for_spec(spec_name):
    tmp_path = '/tmp/optics_procs_procs.txt'
    cmd = f"ps -edalf | grep python | grep -v grep | grep optics | grep ' manager ' | grep {spec_name}  > {tmp_path}"
    os.system(cmd)
    f = open(tmp_path, 'r')
    lines = f.readlines()
    f.close()
    os.system(f'rm {tmp_path}')
    if len(lines) > 1:
        return True
    return False
     
def configure_logging(level):
    optics_info(f'...setting log level to {level}')
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(f'%(levelname)s: %(message)s')
    os.makedirs('optics_logs', exist_ok=True)
    log_path = 'optics_logs/optics_log_' + str(time.time()) + '.log'
    #
    file_handler = logging.FileHandler(filename = log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    stderr_handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(stderr_handler)
    
def usage():
    print("python optics.py manager|run_scenes|stop|scores|erase_results|status|errors|scores|container_run <optics_config>")
    print('        manager - will only work when invoked on ec2b')
    print('        run_scene - will run a scene form any machine if the env is deemed to match the one specified in the config')


if __name__ == '__main__':
    datastore_proximity = get_optics_datastore_proximity()
    
    if not 'OPICS_HOME' in os.environ:
        optics_fatal('OPICS_HOME not defined.  Please "export OPICS_HOME=<parent_of_opics_dir>"')
        
    if len(sys.argv) < 3:
        usage()
        sys.exit()

    if sys.argv[1] not in ['manager', 'run_scenes','stop','scores','erase_results','status','errors', 'container_run','scores']:
        usage()
        sys.exit()

    cmd = sys.argv[1]
    given_optics_spec_path = sys.argv[2]
    optics_spec_path = resolve_given_optics_spec_path(given_optics_spec_path)
    print(f'optics_spec_path: {optics_spec_path}')
    optics_spec = OpticsSpec(optics_spec_path)

    configure_logging(optics_spec.log_level)
    proj            = optics_spec.proj
    version         = optics_spec.version
    controller_type = optics_spec.controller
    spec_name       = optics_spec.name
    
    if cmd == 'manager':
        if not is_running_on_ec2():
            print('ERROR - manager command can only be invoked on ec2a or ec2b')
            sys.exit()
        if is_already_manager_running_for_spec(spec_name):
            optics_fatal("ERROR - manager for this optics spec already running on this machine.  Shut the other one down with 'stop'")
        else:
            print('...running manager...')
            ots = OpticsTestSequencer(optics_spec)
            ots.start()

    elif cmd == 'container_run':
        print('...running scenes...')
        otr = OpticsTestRunner(optics_spec_path, datastore_proximity, TEST_SET_ORDER)
        otr.run()
            
    elif cmd == 'run_scenes':
        if version != 'self_test':
            verify_conda_env_for_project_is_activated(proj)
        print('...running scenes...')
        if version == 'self_test':
            if not is_optics_manager_running_locally(given_optics_spec_path):
                answer = input('no manager running locally - are you self-testing remote?')
                if answer != 'y':
                    print('exiting')
                    sys.exit()
            print('...running self_test')
            otsr = OpticsSelfTestRunner(optics_spec, datastore_proximity, TEST_SET_ORDER)
            otsr.normal_healthy_state_progression()
            otsr.test_gpu_mem_failure()
            otsr.test_timeout_failure()
        else:
            otr = OpticsTestRunner(optics_spec_path, datastore_proximity, TEST_SET_ORDER)
            otr.run()

    elif cmd == 'stop':
        stopper = OpticsStopper(optics_spec)
        stopper.stop_processes()
        sys.exit()

    elif cmd == 'erase_results':
        if not is_running_on_ec2():
            print('ERROR - erase_results is only relevant on ec2a or ec2b')
            sys.exit()
        manager_process = os.popen(f'ps -edalf | grep -v edalf | grep optics | grep {optics_spec}').read()
        if manager_process:
            print(f'[optics]...ERROR: optics manager is running for {given_optics_spec_path} - stop it and try again')
            print(f'[optics]...manager_process {manager_process}')
            sys.exit()
        else:
            optics_results_eraser = OpticsResultsEraser(optics_spec)
            optics_results_eraser.erase_results()
            sys.exit()

    elif cmd == 'status':
        dashboard = OpticsDashboard(datastore_proximity, optics_spec)
        dashboard.show_all()

    elif cmd == 'errors':
        if not is_running_on_ec2():
            print('ERROR - errors command only relevant on ec2a or ec2b')
            sys.exit()
        if proj == 'inter':
            error_details = ErrorDetails(optics_spec)
            error_details.show_errors_by_scene_type_inter()
            error_details.show_error_type_counts_inter()

    elif cmd =='scores':
        optics_scores = OpticsScores(proj,optics_spec)
        optics_scores.show_scores()
        sys.exit()


    else:
        usage()
        sys.exit()
