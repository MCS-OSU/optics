import os

from remote_control.constants import REMOTE_ROOT, TO_USER_REMOTE_DIR, FROM_USER_REMOTE_DIR

if __name__ == "__main__":
    messaging_root = REMOTE_ROOT
    optics_home = os.environ['OPTICS_HOME']
    names_file_path = os.path.join(optics_home, 'remote_control', 'runner_names.txt')
    f = open(names_file_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if line.startswith('#'):
            continue
        name = line.strip()
        user_root = os.path.join(messaging_root, name)
        os.makedirs(user_root, exist_ok=True)
        to_user_dir = os.path.join(user_root, TO_USER_REMOTE_DIR)
        from_user_dir = os.path.join(user_root, FROM_USER_REMOTE_DIR)
        os.makedirs(to_user_dir, exist_ok=True)
        os.makedirs(from_user_dir, exist_ok=True)
        
