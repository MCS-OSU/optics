
import os
import subprocess

class OpticsStopper():
    def __init__(self, optics_spec):
        self.optics_spec = optics_spec
        
        result = subprocess.run(['uname', '-a'], stdout=subprocess.PIPE)
        if not 'Ubuntu' in result.stdout.decode('utf-8'):
            print('only implemented for ubuntu so far')
            print('(worried might derive process number from wrong field)')
            sys.exit()


    def stop_processes(self):
        self.kill_optics_procs_for_command('run_scenes')
        self.kill_systest_scene_runner_for_spec()
        self.kill_optics_procs_for_command('manager')


    def get_unity_child_processes(self,opics_pid):
        cmd = f'ps -edalf | grep -v grep | grep MCS-AI2-THOR-Unity-App | grep {opics_pid} > /tmp/optics_procs_procs.txt'
        os.system(cmd)
        f = open('/tmp/optics_procs_procs.txt', 'r')
        lines = f.readlines()
        f.close()
        # verify the opics_pid is actually in column 4
        result = []
        for line in lines:
            fields = line.split()
            if fields[4] == opics_pid:
                result.append(line)
        return result

    def kill_optics_procs_for_command(self, optics_command):
        cmd = f'ps -edalf | grep python | grep -v grep | grep optics | grep {optics_command} | grep {self.optics_spec.name}  > /tmp/optics_procs_procs.txt'
        print(f'looking for optics.py processes to kill belonging to {optics_command} command for {self.optics_spec.name} ...')
        self.kill_procs_as_per_command(cmd)

    def kill_systest_scene_runner_for_spec(self):
        cmd = f'ps -edalf | grep python | grep -v grep | grep optics_run_scene | grep {self.optics_spec.name} > /tmp/optics_procs_procs.txt'
        print(f'looking for processes to kill belonging to optics_run_scene for  {self.optics_spec.name}  ...')
        self.kill_procs_as_per_command(cmd)

    def kill_procs_as_per_command(self, cmd):
        os.system(cmd)
        f = open('/tmp/optics_procs_procs.txt', 'r')
        lines = f.readlines()
        f.close()
        os.system('rm /tmp/optics_procs_procs.txt')
        for line in lines:
            print('')
            print('...found:')
            fields = line.split()
            opics_pid = fields[3]
            unity_procs = self.get_unity_child_processes(opics_pid)
            for unity_proc in unity_procs:
                print(unity_proc)
                
            print(line)
            answ = input('Enter y to kill: ')
            if answ == 'y':
                for unity_proc in unity_procs:
                    unity_pid = unity_proc.split()[3]
                    cmd = f'kill -9 {unity_pid}'
                    print(cmd)
                    os.system(cmd)
                cmd = f'kill -9 {opics_pid}'
                print(cmd)
                os.system(cmd)
