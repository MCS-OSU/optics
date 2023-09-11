
import os
import subprocess

if __name__ == "__main__":
    cmd = "python timer_for_testing_launch_and_stop.py 2 5&"
    os.system(cmd)
    print("===========================================> Thanks")
    cmd = 'ps -edalf | grep "python timer_for_testing_launch" > temp.txt'
    print(f'cmd is {cmd}')
    os.system(cmd)
    f = open('temp.txt', 'r')
    lines = f.readlines()
    f.close()
    result = ' '.join(lines[0].split())
    pid = result.split(' ')[3]
    
    print(f'\n\npid is {pid}\n\n')
    cmd = f'kill -9 {pid}'
    print(f'cmd is {cmd}')
    os.system(cmd)