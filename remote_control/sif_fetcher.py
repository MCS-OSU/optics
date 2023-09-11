import os

from pathlib import Path
from scripts.ec2.machines import EC2A, EC2B, EC2C, EC2D
from core.utils import remote_get_file_quiet, remote_get_file


class SifFetcher():
    def __init__(self):
        pass 

    def fetch(self, source, sif_name):
        if source == 'a':
            ec2 = EC2A()
        elif source == 'b':
            ec2 = EC2B()
        elif source == 'c':
            ec2 = EC2C()
        elif source == 'd':
            ec2 = EC2D()
        else:
            raise Exception(f'unknown source {source}')
        home_dir = str(Path.home())
        target_dir = os.path.join(home_dir, 'optics_sif_files')
        os.makedirs(target_dir, exist_ok=True)
        

        