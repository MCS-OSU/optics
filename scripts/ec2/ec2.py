
import os
import sys
from scripts.ec2.machines import EC2A, EC2C, EC2D

def verify_2_args(args, cmd, arg1, arg2):
    if not len(args) == 5:
        print(f'{cmd} command has two args: {arg1}  {arg2}')
        sys.exit()

def verify_1_arg(args, cmd, arg1):
    if not len(args) == 4:
        print(f'{cmd} command has one args: {arg1}')
        sys.exit()

def verify_arg_is_file(path):
    if not os.path.isfile(path):
        print(f'{path} is not a file')
        sys.exit()

def verify_arg_is_dir(path):
    if not os.path.isdir(path):
        print(f'{path} is not a dir')
        sys.exit()

def get_legal_limit_for_count(limit_string, count):
    if limit_string=='all':
            range_limit = count
    else:
        if not limit_string.isnumeric():
            print(f'ERROR limit must be numeric : {limit_string}')
            sys.exit()
        limit_int = int(limit_string)
        if limit_int > count:
            range_limit = count
        else:
            range_limit = limit_int
    return range_limit

def usage():
    print('usage:  python ec2.py a|c|d <cmd> <arg1> <arg2>')
    print('                          put_scene <src_path> <dest_dir>')
    print('                          put_scenes <src_path> <dest_dir>')
    print('                          gen_videos <src_dir> all|1|2|...')
    print('                          collect_oracle_data <src_dir> <dest_dir>')
    print('                          get_file <remote_path> <local_dest_dir>')
    print('                          put_file <local_path> <remote_dest_dir>')
  
if __name__ == '__main__':
    

    if len(sys.argv) < 3:
        usage()
        sys.exit()

    if sys.argv[1] != 'a' and sys.argv[1] != 'c' and sys.argv[1] != 'd':
        print('first arg must be a, c, or d to represent ec2a, ec2c, ec2d (the p3 machine) ')
        usage()
        sys.exit()

    if sys.argv[1] == 'a':
        ec2 = EC2A()
    if sys.argv[1] == 'c':
        ec2 = EC2C()
    if sys.argv[1] == 'd':
        ec2 = EC2D()
    
    

    cmd = sys.argv[2]
    if cmd == 'put_scene':
        verify_2_args(sys.argv, 'put_scene', 'src_path', 'dest_dir')
        src_path = sys.argv[3]
        dest_dir = sys.argv[4]
        verify_arg_is_file(src_path)
        ec2.put_scene(src_path, dest_dir)
            
    elif cmd == 'put_scenes':
        verify_2_args(sys.argv, 'put_scene', 'src_path', 'dest_dir')
        src_dir = sys.argv[3]
        dest_dir = sys.argv[4]
        verify_arg_is_dir(src_dir)
        ec2.put_scenes(src_dir, dest_dir)
        
    elif cmd == 'collect_oracle_data':
        verify_2_args(sys.argv, 'collect_oracle_data', 'src_dir', 'dest_dir')
        src_dir = sys.argv[3]
        dest_dir = sys.argv[4]
        verify_arg_is_dir(src_dir)
        ec2.collect_oracle_data_for_pvoe_files(src_dir, dest_dir)

    elif cmd == 'gen_videos':
        verify_2_args(sys.argv, 'gen_videos', 'src_dir', 'limit')
        src_dir = sys.argv[3]
        verify_arg_is_dir(src_dir)
        limit_string = sys.argv[4]
        files = sorted(os.listdir(src_dir))
        range_limit = get_legal_limit_for_count(limit_string, len(files))

        #os.mkdirs(dest_dir)
        for i in range(range_limit):
            file = files[i]
            if not file.endswith('.json'):
                continue
            path = os.path.join(src_dir, file)
            ec2.get_video(path)

            print(f'############################################################################################################')
            print(f'                              {i+1} of {range_limit} videos retrieved')
            print(f'############################################################################################################')

    elif cmd == 'get_file':
        verify_2_args(sys.argv, 'get_file', 'remote_path', 'local_dest_dir')
        remote_path = sys.argv[3]
        local_dest_dir = sys.argv[4]
        verify_arg_is_dir(local_dest_dir)
        ec2.get_file(remote_path, local_dest_dir)


    elif cmd == 'put_file':
        verify_2_args(sys.argv, 'put_file', 'local_path', 'remote_dest_dir')
        local_path = sys.argv[3]
        remote_dest_dir = sys.argv[4]
        verify_arg_is_file(local_path)
        ec2.put_file(local_path, remote_dest_dir)

    else:
        print(f'unknown command: {cmd}')
        usage()
        sys.exit()
    
    
    
