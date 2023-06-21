''' 
code according to this note:
this runs on server
optics/scripts/zip_results.py <spec> incorrect|exception vidyes|vidno <scene_type> 

put results into eval6_systest/<proj>/zips/<spec>_incorrect_vidyes_<scene_type>.zip

reuse the logic for loading the log files that is used by optics scores and iterate through the logs to gather the info needed
'''
import os
import sys
from pathlib import Path
from opics_common.opics_logging import OpicsLogs
from opics_common.scene_type.type_constants import formal_type
from core.optics_dirs import SystestDirectories

class ZipResults:
    def __init__(self, spec, error_type, proj):
        self.spec = spec
        self.error_type = error_type
        self.proj = proj
        self.systest_dirs = SystestDirectories(str(str(Path.home()), self.optics_spec)
        self.proj_log_dir = self.systest_dirs.result_logs_dir
        self.proj_stdout_log_dir = self.systest_dirs.stdout_logs_dir
        self.opics_logs = OpicsLogs()

        for scene_type in formal_type:
            type_dir = os.path.join(self.proj_log_dir, scene_type)
            if os.path.exists(type_dir):
                files = os.listdir(type_dir)
                #print(type_dir)
                for file in files:
                    filepath = os.path.join(type_dir, file)
                    #print(f'log file {filepath}')
                    if os.path.isfile(filepath):
                        # print(f'file:  {filepath}')
                        self.opics_logs.load_file(filepath, proj, scene_type)

    
    def zip_files(self):
        log_paths = []
        stdout_log_paths = []
        for scene_type in self.opics_logs.logs[proj]:
            for log in self.opics_logs.logs[proj][scene_type]:
                if log.exception_info != None:
                    scene_hame = log.scene_name
                    # log_path = os.path.join('/home/ubuntu/eval6_systest/',proj,'versions'....
                    # stdout_log_path = os.path.join(self.proj_stdout_log_dir, scene_type, scene_name, 'stdout.log')
                    #append to each array
                    log_paths.append(log_path)
                    stdout_log_paths.append(stdout_log_path)
        print(f'log_paths: {log_paths}\n')
        print(f'stdout_log_paths: {stdout_log_paths}')


if __name__ == "__main__":
    spec = sys.argv[1]
    error_type = sys.argv[2]
    scene_type = sys.argv[3]
    if error_type not in ['incorrect', 'exception']:
        print('error_type must be incorrect or exception')
        sys.exit(1)
    if scene_type not in ['vidyes', 'vidno']:
        print('scene_type must be vidyes or vidno')
        sys.exit(1)
    
    print('spec: ', spec)
    print('error_type: ', error_type)
    print('scene_type: ', scene_type)
    zip_results = ZipResults(spec, error_type, proj)
    zip_results.zip_files()






    
        
        
# def zipresults():
#     spec = sys.argv[1]
#     error_type = sys.argv[2]
#     scene_type = sys.argv[3]
#     if error_type not in ['incorrect', 'exception']:
#         print('error_type must be incorrect or exception')
#         sys.exit(1)
#     if scene_type not in ['vidyes', 'vidno']:
#         print('scene_type must be vidyes or vidno')
#         sys.exit(1)
    
#     print('spec: ', spec)
#     print('error_type: ', error_type)
#     print('scene_type: ', scene_type)


