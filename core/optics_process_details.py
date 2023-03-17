import subprocess
from utils import is_running_on_ec2a, is_running_on_ec2b
from core.constants import EC2A_URL, EC2B_URL, EC2A_UNAME_OUTPUT, EC2B_UNAME_OUTPUT
class OpticsProcessDetails: 
    def __init__(self, machine_name):
        self.machine_name = machine_name

    def run_command_and_return_output(self, command):
        val = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #getting the output
        output, err = val.communicate()
        #decoding the output
        output = output.decode('utf-8')
        return output

    def get_optics_manager_details(self):
        manager_machine = '' 
        if self.machine_name == 'ec2a' or self.machine_name == 'local':
            command = f'ssh {EC2B_URL} ps -edalf | grep -v edalf | grep optics | grep manager'
            manager_machine = 'ec2b'        
        else:
            command = f'ps -edalf | grep -v edalf | grep optics | grep manager'
            manager_machine = 'ec2b'

        output = self.run_command_and_return_output(command)
        output = output.split()
        manager_process_list = []
        for i in range(len(output)):
            if 'specs/' in output[i]:
                manager_process_list.append(output[i])   
        return manager_process_list, manager_machine
    
    def get_optics_test_runner_details(self):
        command_local = f'ps -edalf | grep -v edalf | grep run_scenes'        
        if self.machine_name == 'ec2a':
            command_ec2a = command_local
            command_ec2b = f'ssh {EC2B_URL} ps -edalf | grep -v edalf | grep optics | grep run_scenes'
        elif self.machine_name == 'local':
            command_ec2a = f'ssh {EC2A_URL} ps -edalf | grep -v edalf | grep optics | grep run_scenes'
            command_ec2b = f'ssh {EC2B_URL} ps -edalf | grep -v edalf | grep optics | grep run_scenes'
        else: # ec2b
            command_ec2a = f'ssh {EC2A_URL} ps -edalf | grep -v edalf | grep optics | grep run_scenes'
            command_ec2b = command_local
        
        output_ec2a = self.run_command_and_return_output(command_ec2a)
        output_ec2a = output_ec2a.split()
        test_runner_process_list_ec2a = []
        for i in range(len(output_ec2a)):
            if 'specs/' in output_ec2a[i]:
                test_runner_process_list_ec2a.append(output_ec2a[i])
                

        output_ec2b = self.run_command_and_return_output(command_ec2b)
        output_ec2b = output_ec2b.split()
        test_runner_process_list_ec2b = []
        for i in range(len(output_ec2b)):
            if 'specs/' in output_ec2b[i]:
                test_runner_process_list_ec2b.append(output_ec2b[i]) 
        
        return test_runner_process_list_ec2a, test_runner_process_list_ec2b
    
    def get_other_python_processes(self):
        
        command_ec2b = f'ssh {EC2B_URL}ps -edalf | grep -v edalf | grep python'
        command_ec2a = f'ssh {EC2A_URL}ps -edalf | grep -v edalf | grep python'
        output_ec2a = self.run_command_and_return_output(command_ec2a)
        output_ec2b = self.run_command_and_return_output(command_ec2b)
        
        return output_ec2a, output_ec2b
    
    def get_disk_space(self):
        command_ec2a = f'ssh {EC2A_URL} df --total -h'
        command_ec2b = f'ssh {EC2B_URL} df --total -h'

        #for ec2a
        output_ec2a = self.run_command_and_return_output(command_ec2a)
        output_ec2a = output_ec2a.split('\n')
        output_ec2a = output_ec2a[-2].split()
        
        #for ec2b
        output_ec2b = self.run_command_and_return_output(command_ec2b)
        output_ec2b = output_ec2b.split('\n')
        output_ec2b = output_ec2b[-2].split()

        return output_ec2a, output_ec2b
    
    def add_break_line(self):
        print('----------------------------------------------')

    def show_manager_process_details(self):
        manager_process_list, manager_machine_name = self.get_optics_manager_details()
        self.add_break_line()
        print('managers: ', len(manager_process_list))
        self.add_break_line()
        print( manager_machine_name)
        for manager_process in manager_process_list:
            print('\t',manager_process)
        print('\n')
       
    
    def show_test_runner_process_details(self):
        test_runner_process_list_ec2a, test_runner_process_list_ec2b = self.get_optics_test_runner_details()
        self.add_break_line()
        print('test_runners : ', len(test_runner_process_list_ec2a) + len(test_runner_process_list_ec2b)) 
        self.add_break_line()
        # print('test_runner_process_list_ec2a: ', len(test_runner_process_list_ec2a))
        if len(test_runner_process_list_ec2a) > 0:
            for test_runner_process in test_runner_process_list_ec2a:
                print('\t',test_runner_process)
        else:
            print('\t','No test_runner process is running on ec2a')

        # print('test_runner_process_list_ec2b: ', len(test_runner_process_list_ec2b))
        if len(test_runner_process_list_ec2b) > 0:
            for test_runner_process in test_runner_process_list_ec2b:
                print('\t',test_runner_process)
        else:
            print('\t','No test_runner process is running on ec2b')
        print('\n')
    
    def show_disk_space_details(self):
        title = ['Filesystem','Used','Avail','Use%','Mounted on']
        disk_space_ec2a, disk_space_ec2b = self.get_disk_space()

        self.add_break_line()
        print('\t\tDISK SPACE')
        self.add_break_line()
        print('On EC2A Machine:')
        print('\t'.join(title))
        print('\t'.join(disk_space_ec2a))
        print('On EC2B Machine:')
        print('\t'.join(title))
        print('\t'.join(disk_space_ec2b))
        print('\n')   

    def what_is_going_on(self):
        # Show manager processes
        self.show_manager_process_details()
        # Show test_runner processe
        self.show_test_runner_process_details()
        # Show disk space
        self.show_disk_space_details()
        # Show other python processes
        # self.show_other_python_processes()


if __name__ == '__main__':
    machine_name = None
    if is_running_on_ec2a():
        machine_name = 'ec2a'
    elif is_running_on_ec2b():
        machine_name = 'ec2b'
    else: 
        machine_name = 'local'
    process_details = OpticsProcessDetails(machine_name)
    process_details.what_is_going_on()
   