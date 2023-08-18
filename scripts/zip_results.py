import os
import sys
from pathlib import Path
from opics_common.opics_logging.opics_logs import OpicsLogs
from opics_common.scene_type.type_constants import formal_type
from core.optics_dirs import SystestDirectories
from opics_common.opics_logging.scene_log import SceneLog, PvoeSceneLog, AvoeSceneLog, InterSceneLog
class ZipResults:
    def __init__(self, spec, error_type, scene_type, video_type):
        self.spec = spec.split('/')[-1]
        self.error_type = error_type
        self.scene_type = scene_type
        self.proj = self.spec.split('_')[0]
        self.video_type = video_type
        # print(f'proj: {self.proj}')
        self.spec_for_path = self.spec.split(self.proj+'_')[1][:-4]
        print(f'spec_path: {self.spec_for_path}')
        self.proj_log_dir = os.path.join('/home/ubuntu/eval6_systest', self.proj, 'versions', self.spec_for_path, 'logs')
        self.proj_stdout_log_dir = os.path.join('/home/ubuntu/eval6_systest', self.proj, 'versions', self.spec_for_path, 'stdout_logs')
        self.opics_logs = OpicsLogs()

        type_dir = os.path.join(self.proj_log_dir, self.scene_type)
        # print(f'type_dir: {type_dir}')
        if os.path.exists(type_dir):
            files = os.listdir(type_dir)
            # print(type_dir)
            for file in files:
                filepath = os.path.join(type_dir, file)
                # print(f'log file {filepath}')
                if os.path.isfile(filepath):
                    # print (f'file:  {filepath}')
                    self.opics_logs.load_file(filepath, self.proj, scene_type)

    # def get_incorrect_scenes(self):
    #     if self.proj == 'pvoe':
            

    def get_exception_scenes(self):
        log_paths = []
        stdout_log_paths = []
        for scene_type in self.opics_logs.logs[self.proj]:
            for log in self.opics_logs.logs[self.proj][scene_type]:
                if log.exception_info is not None:
                    scene_name = log.scene_name
                    if self.scene_type != 'all':
                        # log_path = os.path.join(self.proj_log_dir,self.scene_type,f'{log}.txt')
                        stdout_log_path = os.path.join( self.proj_stdout_log_dir,self.scene_type,f'{scene_name}_stdout.txt')
                        # print(f'stdout_log_path: {stdout_log_path}')
                        
                        # log_paths.append(log_path)
                        stdout_log_paths.append(stdout_log_path)
        # print(f'log_paths: {log_paths}\n')
        # print(f'stdout_log_paths: {stdout_log_paths}')
        return log_paths, stdout_log_paths


    def get_scenes_to_zip(self):
        log_paths = []
        stdout_log_paths = []

        if self.error_type == 'incorrect':
            pass
        elif self.error_type == 'exception':
            log_paths, stdout_log_paths = self.get_exception_scenes()

        return log_paths, stdout_log_paths
    
    
    def zip_files(self):
        log_paths = []
        stdout_log_paths = []
        
        
        #zip files commented out
        zip_file_name = f'{self.spec_for_path}_{self.error_type}_{self.scene_type}.zip'
        zip_dir_path = os.path.join('/home/ubuntu/eval6_systest/',self.proj,'zips')
        os.makedirs(zip_dir_path, exist_ok=True)
        zip_file_path = os.path.join('/home/ubuntu/eval6_systest/',self.proj,'zips',zip_file_name)
        cmd = f'zip -r -q {zip_file_path} {" ".join(stdout_log_paths)}'
        # print(f'cmd: {cmd}')
        os.system(cmd)


if __name__ == "__main__":
    spec = sys.argv[1]
    error_type = sys.argv[2]
    scene_type = sys.argv[3]
    video_type = sys.argv[4]

    if error_type not in ['incorrect', 'exception']:
        print('error_type must be incorrect or exception')
        sys.exit(1)
    # if video_type not in ['vidyes', 'vidno']:
    #     print('scene_type must be vidyes or vidno')
    #     sys.exit(1)
    
    print('spec: ', spec)
    print('error_type: ', error_type)
    print('scene_type: ', scene_type)
    print('video_type: ', video_type)
    zip_results = ZipResults(spec, error_type, scene_type, video_type)
    zip_results.zip_files()






    
        
        
# def set_paths(self, proj, spec)
# 
