
import subprocess
import time
class GPU():
    def __init__(self):
        pass

    def is_available(self):
        cmd = 'nvidia-smi'
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode('utf-8')
        lines = output.split('\n')
        mem_line = lines[8]
        used = mem_line.split()[9]
        total = mem_line.split()[11]
        used = int(used.split('MiB')[0])
        total = int(total.split('MiB')[0])
        avail = total - used
        return avail > 4000

    def print_mem_line(self):
        cmd = 'nvidia-smi'
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode('utf-8')
        lines = output.split('\n')
        mem_line = lines[9]
        print(mem_line)

if __name__ == '__main__':
    gpu = GPU()
    for i in range(6000):
        gpu.print_mem_line()
        time.sleep(2)
    