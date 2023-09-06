import os, sys
import time
from core.constants import EC2A_URL, EC2C_URL, EC2D_URL
import subprocess

class EC2Results():
    def __init__(self, name, url, root_dir):
        if not 'PEM_PATH' in os.environ:
            print('ERROR:  must set env var PEM_PATH to point to your copy of shared-with-opics.pem')
            sys.exit()
    
        pem_path = os.environ['PEM_PATH']
        if not os.path.exists(pem_path) or not pem_path.endswith('.pem'):
            print(f'ERROR:  PEM_PATH env var does not point to a pem file: {pem_path}')
            sys.exit()
        self.pem_path = os.environ['PEM_PATH']
        self.name = name
        self.url = url
        self.root_dir = root_dir
        self.script_dir = os.path.join(root_dir,'scripts')
        self.pvoe_script_dir = os.path.join(self.script_dir,'pvoe' )
        self.root_scene_dir = root_dir + '/s'
        
    def get_specs_for_project(self, proj):
        return self.get_remote_result_as_lines(f'ls -1 /home/ubuntu/eval6_systest/{proj}/versions')

    def get_file_contents_for_rel_path(self, proj, rel_path):
        s = self.get_remote_result(f'cat /home/ubuntu/eval6_systest/{proj}/versions/{rel_path}')
        return s
   
    def get_remote_scores(self, spec_name):
        lines = self.get_remote_result(f'python optics.py scores specs/{spec_name}')
        print(lines)
        return lines
        
    def get_optics_pythonpath(self):
        return f'{self.root_dir}:{self.root_dir}/opics_common'

    def get_optics_home(self):
        return self.root_dir

    def get_remote_result_as_lines(self, command):
        return self.get_remote_result(command).split('\n')

    def get_remote_result(self, command):
        python_path = self.get_optics_pythonpath()
        optics_home = self.get_optics_home()
        optics_datastore = os.environ['OPTICS_DATASTORE']
        exports_string = f'export OPTICS_HOME={optics_home};export PYTHONPATH={python_path};export OPTICS_DATASTORE={optics_datastore}'
        invoke_string = f'cd {self.root_dir};{command}'
        return subprocess.check_output(f'ssh -i {self.pem_path} -l ubuntu {self.url} "{exports_string};{invoke_string}"', shell=True).decode('utf-8')

    def retrieve_video(self, proj, parent_rel_path, rel_path):
        remote_src_path = f'/home/ubuntu/eval6_systest/{proj}/versions/{rel_path}'
        try:
            cwd = os.getcwd()
            tmp_dest_path = '/tmp/' + rel_path
            os.makedirs('/tmp/' + parent_rel_path, exist_ok=True)
            local_dest_path = f'{cwd}/static/media/{proj}/{rel_path}'
            url_rel_path = f'media/{proj}/{rel_path}'
            os.makedirs(os.path.dirname(local_dest_path), exist_ok=True)
            subprocess.check_output(f'scp -i {self.pem_path} -r {self.url}:{remote_src_path} {tmp_dest_path}', shell=True)
            print(f'ffmpeg -i {tmp_dest_path} -vcodec h264 -y {local_dest_path}')
            os.system('ffmpeg -i ' + tmp_dest_path + ' -vcodec h264 -y ' + local_dest_path)
            os.system('rm ' + tmp_dest_path)
            return url_rel_path
        except:
            return None

    # def get_scene_types_for_run(self, proj, spec_name):
    #     return self.get_remote_result_as_lines(f'ls -1 /home/ubuntu/eval6_systest/{proj}/versions/{spec_name}/stdout_logs')
    def get_correctness_for_scene_type(self, proj, run, scene_type):
        return self.run_remote_script('flask_remote_results', 'get_correctness_for_scenes.py', f'{proj} {run} {scene_type}')

    def get_remote_script_result_as_lines(self, rel_dir, script_name, args_as_string):
        return self.run_remote_script(rel_dir,script_name, args_as_string).split('\n')

    def run_remote_script(self, rel_dir, script_name, args_as_string):
        python_path = self.get_optics_pythonpath()
        optics_home = self.get_optics_home()
        optics_datastore = os.environ['OPTICS_DATASTORE']
        exports_string = f'export OPTICS_HOME={optics_home};export PYTHONPATH={python_path};export OPTICS_DATASTORE={optics_datastore}'
        if rel_dir == '':
            invoke_string = f'cd {self.root_dir};python3 {script_name} {args_as_string}'
        else:
            invoke_string = f'cd {self.root_dir};python3 {rel_dir}/{script_name} {args_as_string}'
        print(f'sending remote invocation: {invoke_string}')
        cmd = f'ssh -i {self.pem_path} -l ubuntu {self.url} "{exports_string};{invoke_string}"'
        #print(f'\n\ncmd: {cmd}\n\n')
        return subprocess.check_output(cmd, shell=True).decode('utf-8')


    def get_active_optics_data(self):
        return self.run_remote_script('flask_remote_results','get_active_optics_data_tree.py', '')


class EC2DResults(EC2Results):
    def __init__(self):
        EC2Results.__init__(self, 'ec2d', EC2D_URL,  '/home/ubuntu/main_optics')
