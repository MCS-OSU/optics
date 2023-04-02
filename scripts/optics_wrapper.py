import sys, os
import threading, time
from remote_control.optics_run_monitor import OpticsRunMonitor

def start_container(sif_path):
    run_name = os.path.basename(sif_path).split('.')[0]
    proj = run_name.split('_')[0]
    if proj == 'inter':
        run_cmd = f'singularity run --nv {sif_path} optics scene_type_provided'
    else:
        run_cmd = f'singularity run --nv {sif_path} optics'
    print(f'running {run_name}...')
    os.system(run_cmd)


def usage():
    print('usage: python3 optics_wrapper.py <cmd> ...')
    print('         where <cmd> can be ')
    #print('               get          a|b|c|d  <run_name> # fetches the .sif file')
    #print('               get_then_run a|b|c|d  <run_name> # fetches the .sif file and runs it')
    print('               run          <sif_path>  # runs a container already downloaded')
    print('')
    sys.exit(1)

if __name__=='__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit()

    cmd = sys.argv[1]
    if not cmd in ['get', 'get_then_run', 'run']:
        usage()
        sys.exit()

    # if cmd == 'get':
    #     if len(sys.argv) != 4:
    #         usage()
    #         sys.exit()
    #     source = sys.argv[2]
    #     run_name = sys.argv[3]
    #     if not run_name.endswith('.sif'):
    #         run_name += '.sif'
    #     print(f'fetching {run_name} from {source}...')
    #     sif_fetcher = SifFetcher()

    if cmd == 'run':
        if len(sys.argv) != 3:
            usage()
            sys.exit()
        sif_path = sys.argv[2]
        if not sif_path.endswith('.sif'):
            sif_path += '.sif'
        if not os.path.exists(sif_path):
            print(f'file not found: {sif_path}')
            sys.exit()
        run_name = os.path.basename(sif_path).split('.')[0]
        keep_restarting = True
        while keep_restarting:
            threading.Thread(target=start_container, args=(sif_path), daemon=True).start()
            orm = OpticsRunMonitor(run_name)
            optics_run_ended_healthily = orm.monitor_run()
            if optics_run_ended_healthily:
                keep_restarting = False
            else:
                print('restarting hung or crashed optics run in 3 sec...')
                time.sleep(5)