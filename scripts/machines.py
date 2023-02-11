import os
import time
from core.constants import EC2A_URL, EC2B_URL

class EC2():
    def __init__(self, name, url, root_dir):
        self.name = name
        self.url = url
        self.root_dir = root_dir
        self.script_dir = os.path.join(root_dir,'scripts')
        self.pvoe_script_dir = os.path.join(self.script_dir,'pvoe' )
        self.root_scene_dir = root_dir + '/s'


    def ensure_remote_dir(self,dir):
        os.system(f'ssh -i shared-with-opics.pem {self.url} "mkdir -p {dir}"')
    
    def ensure_remote_scene_dir(self,dir):
        #ssh -i shared-with-opics.pem  ubuntu@3.221.218.227 "cd /home/ubuntu/eval6/s;mkdir $1"
        os.system(f'ssh -i shared-with-opics.pem {self.url} "cd {self.root_scene_dir};mkdir -p {dir}"')

    def put_scenes(self, src_dir, dest_scene_dir):
        #scp -i shared-with-opics.pem $1/* ubuntu@3.221.218.227:/home/ubuntu/eval6/s/$1
        dest_dir = f'{self.root_scene_dir}/{dest_scene_dir}'
        self.ensure_remote_scene_dir(dest_dir)
        print(f'copying {src_dir}/* to ec2b {dest_dir}')
        os.system(f'scp -i shared-with-opics.pem {src_dir}/* {self.url}:{dest_dir}')
        
    def put_scene(self, src_path, dest_scene_dir):
        #scp -i shared-with-opics.pem $1 ubuntu@3.221.218.227:/home/ubuntu/eval6/s/$1
        self.ensure_remote_scene_dir(dest_scene_dir)
        dest_dir = f'{self.root_scene_dir}/{dest_scene_dir}'
        self.put_file(src_path, dest_dir)

    def put_file(self, src_path, dest_dir):
        print(f'copying {src_path} to {self.name} {dest_dir}')
        os.system(f'scp -i shared-with-opics.pem {src_path} {self.url}:{dest_dir}')

    def get_file(self,remote_src_path, local_dest_dir):
        print(f'copying {remote_src_path} from {self.name} to {local_dest_dir}')
        fname = os.path.basename(remote_src_path)
        os.system(f'scp -i shared-with-opics.pem  {self.url}:{remote_src_path} .')
        os.system(f'mv {fname} {local_dest_dir}')

    def delete_remote_dir(self, dir):
        print(f'deleting {dir} on {self.name}')
        os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "rm -rf {dir}"')

    def verify_ground_truth_file_present(self, root_dir, scene_name):
        
        scene_collection_dir_path = os.path.join(root_dir, scene_name)
        scene_collection_dir_contents = os.listdir(scene_collection_dir_path)
        if not 'gt.txt' in scene_collection_dir_contents:
            print(f'ERROR: {scene_collection_dir_path} does not have a gt.txt file')
            return False
        else:
            print(f'{scene_collection_dir_path} gt.txt file verified')
            return True

    def collect_oracle_data_for_pvoe_files(self, src_scene_dir_local, dest_dir_local):
        timestr = time.strftime("%m%d-%H%M%S")
        tmp_dir = f'/home/ubuntu/eval6/scratch/dc_{timestr}'
        print(f'...collecting oracle data for pvoe files in {src_scene_dir_local} to {dest_dir_local} in tmp dir {tmp_dir}')
        self.ensure_remote_dir(tmp_dir)
        dest_dir_local_logs = dest_dir_local + '_logs'
        os.system(f'mkdir -p {dest_dir_local}')
        os.system(f'mkdir -p {dest_dir_local_logs}')
        files = os.listdir(src_scene_dir_local)
        total = len(files)
        print(f'...found {total} files')
        for i in range(total):
            file = files[i]
            print(f'...collecting oracle data for file {i + 1} of {total} : {file}')
            if file.endswith('.json'):
                scene_path = os.path.join(src_scene_dir_local, file)
                print(f'...path is {scene_path}')
                # copy scene to remote tmp_dir on ec2
                self.put_file(scene_path, tmp_dir)
                # run data collection on that one scene
                scene_name = file.split('.')[0]
                remote_pathname = tmp_dir + '/' + file 
                log_path = tmp_dir + '/' + scene_name + '.log'
                shell_script_invocation = f'cd ~/eval6/scripts/ec2/remote;./collect_oracle_data_for_pvoe_scene.sh {remote_pathname} {tmp_dir} {log_path}'
                print('...running command: ' + shell_script_invocation)
                os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "{shell_script_invocation}"')
                # zip up the result
                os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "cd {tmp_dir};zip -r {scene_name}.zip {scene_name}"')
                # bring that back to the dest_dir 
                self.get_file(tmp_dir + '/' + scene_name + '.zip', dest_dir_local)
                # bring back the log file
                self.get_file(tmp_dir + '/' + scene_name + '.log', dest_dir_local_logs)
                # delete it on the other side
                os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "rm -rf {tmp_dir}/*"')
                # unzip it locally
                os.system(f'unzip -o {dest_dir_local}/{scene_name}.zip -d {dest_dir_local}')
                # delete the zip file
                os.system(f'rm {dest_dir_local}/{scene_name}.zip')
                if not self.verify_ground_truth_file_present(dest_dir_local, scene_name):
                    print('ERROR: missing ground truth file')
                    return
        # delete the tmp dir on the other side
        self.delete_remote_dir(tmp_dir)
        # zip the set
        dirname_dest = os.path.basename(dest_dir_local)
        os.system(f'cd {dest_dir_local};cd ..;zip -r {dirname_dest}.zip {dirname_dest}')

                



    def get_video(self,path):
        src_dirname = os.path.dirname(path)
        scene_name = os.path.basename(path).split('.')[0]
        json_fname = scene_name + '.json'
        print(f'getting video for file {json_fname} in dir {src_dirname}')
        # local side
        local_dest_dir = src_dirname + '_videos'
        if not os.path.isdir(local_dest_dir):
            os.makedirs(local_dest_dir)

        # remote side
        tmp = 'tmp_video'
        self.put_scene(path, tmp)
        tmp_video_dir = os.path.join(self.root_scene_dir, tmp)
        #cd_cmd = f'cd {self.root_scene_dir}/tmp_video'
        #headless_cmd = 'opics_eval6'
        #env_setup_cmd = 'conda activate env_pvoe'
        #cd_cmd = f'cd {self.pvoe_script_dir}'
        #mk_video_cmd = f'python make_scene_video.py --scene {tmp_video_dir}/{json_fname} --out_dir {tmp_video_dir}'
        mk_video_cmd = f'cd ~/eval6/scripts/ec2/remote;./create_video.sh {json_fname}'
        print(f'invoking: {mk_video_cmd}')

        #os.system(f'ssh -i shared-with-opics.pem {self.url} "bash;{headless_cmd};{env_setup_cmd};{cd_cmd};{mk_video_cmd}" > video_make.log')
        os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "{mk_video_cmd}" 2>&1 > video_make.log')
        self.get_file(f'{tmp_video_dir}/{scene_name}/RGB/{scene_name}.mp4', local_dest_dir)
        os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "rm -rf {tmp_video_dir}/*" ')

    def show_running_scenes(self):
        print('')
        print(f'{self.name} running scenes:')
        os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "ps -ef | grep run_opics_scene.py | grep -v \' cd \' | grep -v grep "')

    def show_disk_space(self):
        print('')
        print(f'{self.name} disk space:')
        os.system(f'ssh -i shared-with-opics.pem -l ubuntu {self.url} "df -h | grep xvda1"')

class EC2B(EC2):
    def __init__(self):
        EC2.__init__(self, 'ec2b', EC2B_URL,  '/home/ubuntu/eval6')

class EC2A(EC2):
    def __init__(self):
        EC2.__init__(self, 'ec2a', EC2A_URL,  '/home/ubuntu/eval6')