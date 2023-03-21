import os, sys

def publish_usage():
    print('usage:  python publish_container a|b|c|d <optics_spec_path>')

if __name__ == '__main__':
    if not 'OPTICS_HOME' in os.environ:
        print('OPTICS_HOME is not defined - please set it to the root of the optics_pull')
        sys.exit()

    optics_home = os.environ['OPTICS_HOME']
    if len(sys.argv) < 3:
        publish_usage()
        sys.exit()
    machine = sys.argv[1]
    if not machine in ['a','b','c','d']:
        print('machine name should be a for ec2a, b for ec2b,  c for ec2c,  or d for ec2d')
        publish_usage()
        sys.exit()

    spec_path = sys.argv[2]
    if not os.path.exists(spec_path):
        print(f'given spec path {spec_path} does not exist')
        publish_usage()
        sys.exit()

    spec_name= os.path.basename(spec_path).split('.')[0]
    sif_path = os.path.join(optics_home, 'apptainer', 'sifs', f'{spec_name}.sif')
    if not os.path.exists(sif_path):
        print(f'no sif file for spec {spec_name} exists in {os.dirname(sif_path)}')
        sys.exit()
    print('file exists - uploading...')
    cmd = f'python ec2.py {machine} put_file {sif_path} /home/ubuntu/containers'
    print(f'running this command: {cmd}')
    os.system(cmd)