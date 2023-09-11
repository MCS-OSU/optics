import sys, os
from scripts.ec2.machines import EC2A

def usage():
    print('Usage: python remote_results.py scores <spec_path>')
    print('       (other commands may be added later)')
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit()

    cmd = sys.argv[1]
    if not cmd in ['scores']:
        usage()
        sys.exit()

    spec_path = sys.argv[2]
    if not os.path.exists(spec_path):
        print(f'ERROR:  Spec file {spec_path} does not exist')
        sys.exit()

    spec_name = os.path.basename(spec_path)
    if cmd == 'scores':
        ec2x = EC2A()
        
        ec2x.print_remote_scores(spec_name)
    