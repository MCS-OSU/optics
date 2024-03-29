import subprocess
import os
# from optics import resolve_given_optics_spec_path
from optics_results.optics_dashboard import OpticsDashboard
from core.utils import is_running_on_ec2a, is_running_on_ec2c, is_running_on_ec2d
from core.utils import get_optics_datastore_proximity, get_public_key_path
from core.constants import EC2A_URL, EC2C_URL,EC2D_URL
from core.optics_spec_loader           import OpticsSpec

class OpticsProcessDetails: 
    def __init__(self, machine_name):
        self.machine_name = machine_name
        self.public_key = get_public_key_path()

    def test_runner_process_details(self, command):
        test_runner_process_list = []
        output = self.run_command_and_return_output(command)
        output = output.split() 
        for i in range(len(output)):
            if 'specs/' in output[i]:
                test_runner_process_list.append(output[i])
        return test_runner_process_list
    
    def display_trun_process_list(self, trun_process_list, machine_name):
        print(f' Machine Name: {machine_name}')
        if len(trun_process_list) > 0:
            for test_runner_process in trun_process_list:
                print('\t',test_runner_process)
        else:
            print('\t',f'No test_runner process is running on {machine_name}')
        print('\n')
    
    def resolve_given_optics_spec_path(self,given_path):
        if given_path.startswith('/'):
            return given_path
        return os.path.join(os.environ['OPTICS_HOME'], given_path)
    def add_break_line(self):
        print('----------------------------------------------')

    def run_command_and_return_output(self, command):
        val = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #getting the output
        output, err = val.communicate()
        #decoding the output
        output = output.decode('utf-8')
        return output

    def trim_output(self, output_command, output_length):
        python_list_ec2c = output_command.split()
        trimmed_output = []
        for i in range(len(python_list_ec2c)):
            if python_list_ec2c[i] == 'python':
                process_line = python_list_ec2c[i+1:i+7] if i+7 < len(python_list_ec2c) else python_list_ec2c[i+1:]
                process_line_joined = " ".join(process_line)
                # For debugging
                # print(f'process_line_joined: {process_line_joined}')
                if len(process_line_joined) == 0 or 'manager' in process_line_joined or 'run_scene' in process_line_joined:
                    break
                if len(process_line_joined) < output_length:
                    output_length = process_line_joined
                trimmed_output.append(process_line_joined[:output_length])
        
        return trimmed_output
    def get_optics_manager_details(self):
        manager_machine = '' 
        if self.machine_name == 'local' or self.machine_name == 'ec2c' or self.machine_name == 'ec2d':
            command = f'ssh -i {self.public_key} {EC2A_URL} ps -edalf | grep -v edalf | grep optics | grep manager'
            manager_machine = 'ec2a'        
        
        else:
            command = f'ps -edalf | grep -v edalf | grep optics | grep manager'
            manager_machine = 'ec2a'

        output = self.run_command_and_return_output(command)
        output = output.split()
        manager_process_list = []
        for i in range(len(output)):
            if 'specs/' in output[i]:
                manager_process_list.append(output[i])   
        return manager_process_list, manager_machine
    
    def get_optics_test_runner_details(self):
        command_local = f'ps -edalf | grep -v edalf | grep run_scene'        
        if self.machine_name == 'ec2a':
            command_ec2a = command_local
            command_ec2c = f'ssh -i {self.public_key} {EC2C_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'
            command_ec2d = f'ssh {EC2D_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'

        elif self.machine_name == 'local':
            command_ec2a = f'ssh -i {self.public_key} {EC2A_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'
            command_ec2c = f'ssh -i {self.public_key} {EC2C_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'
            command_ec2d = f'ssh {EC2D_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'

        elif self.machine_name == 'ec2c':
            command_ec2a = f'ssh -i {self.public_key} {EC2A_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'
            command_ec2c = command_local
            command_ec2d = f'ssh {EC2D_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'

        else: #self.machine_name == 'ec2d':
            command_ec2a = f'ssh -i {self.public_key} {EC2A_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'
            command_ec2c = f'ssh -i {self.public_key} {EC2C_URL} ps -edalf | grep -v edalf | grep optics | grep run_scene'
            command_ec2d = command_local

    

        test_runner_process_list_ec2a = self.test_runner_process_details(command_ec2a)
        test_runner_process_list_ec2c = self.test_runner_process_details(command_ec2c)
        test_runner_process_list_ec2d = self.test_runner_process_details(command_ec2d)
        
        return test_runner_process_list_ec2a, test_runner_process_list_ec2c, test_runner_process_list_ec2d
    
    def get_other_python_processes(self):
        
        command_ec2a = f'ssh -i {self.public_key} {EC2A_URL} ps -edalf | grep -v edalf | grep python'
        command_ec2c = f'ssh -i {self.public_key} {EC2C_URL} ps -edalf | grep -v edalf | grep python'
        command_ec2d = f'ssh -i {self.public_key} {EC2D_URL} ps -edalf | grep -v edalf | grep python'
        output_ec2a = self.run_command_and_return_output(command_ec2a)
        output_ec2c = self.run_command_and_return_output(command_ec2c)
        output_ec2d = self.run_command_and_return_output(command_ec2d)
        
        output_ec2c = self.trim_output(output_ec2c, 30)
        output_ec2a = self.trim_output(output_ec2a, 30)
        output_ec2d = self.trim_output(output_ec2d, 30)
        
        return output_ec2a, output_ec2c, output_ec2d
    
    def get_disk_space(self):
        command_ec2a = f'ssh -i {self.public_key} {EC2A_URL} df --total -h'
        # print(f'command_ec2a: {command_ec2a}')
        command_ec2c = f'ssh -i {self.public_key} {EC2C_URL} df --total -h'
        command_ec2d = f'ssh -i {self.public_key} {EC2D_URL} df --total -h'

        #for ec2a
        output_ec2a = self.run_command_and_return_output(command_ec2a)
        # print(f'output_ec2a: {output_ec2a}')
        output_ec2a = output_ec2a.split('\n')
        output_ec2a = output_ec2a[-2].split()
        
        #for ec2c
        output_ec2c = self.run_command_and_return_output(command_ec2c)
        output_ec2c = output_ec2c.split('\n')
        output_ec2c = output_ec2c[-2].split()

        #for ec2d
        output_ec2d = self.run_command_and_return_output(command_ec2d)
        output_ec2d = output_ec2d.split('\n')
        output_ec2d = output_ec2d[-2].split()

        return output_ec2a, output_ec2c, output_ec2d
        
    

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
        test_runner_process_list_ec2a, test_runner_process_list_ec2c, test_runner_process_list_ec2d = self.get_optics_test_runner_details()
        self.add_break_line()
        print('test_runners : ', len(test_runner_process_list_ec2a) + len(test_runner_process_list_ec2c) + len(test_runner_process_list_ec2d))
        self.add_break_line()
        # print('test_runner_process_list_ec2a: ', len(test_runner_process_list_ec2a))
        self.display_trun_process_list(test_runner_process_list_ec2a, 'ec2a')
        self.display_trun_process_list(test_runner_process_list_ec2c, 'ec2c')
        self.display_trun_process_list(test_runner_process_list_ec2d, 'ec2d')
        
        # self.add_break_line()
        print('\n')

    def show_disk_space_details(self):
        title = ['Filesystem','Used','Avail','Use%','Mounted on']
        disk_space_ec2a, disk_space_ec2c, disk_space_ec2d = self.get_disk_space()

        self.add_break_line()
        print('\t\tDISK SPACE')
        self.add_break_line()
        print('On EC2A Machine:')
        print('\t'.join(title))
        print('\t'.join(disk_space_ec2a))
        print('\n')
        print('On EC2C Machine:')
        print('\t'.join(title))
        print('\t'.join(disk_space_ec2c))
        print('\n')
        print('On EC2D Machine:')
        print('\t'.join(title))
        print('\t'.join(disk_space_ec2d))
        print('\n')

    def show_other_python_processes(self):
        other_python_processes_ec2a,other_python_processes_ec2c,other_python_processes_ec2d = self.get_other_python_processes()
        
        self.add_break_line()
        print('\t\tOTHER PYTHON PROCESSES')
        self.add_break_line()
        print('On EC2A Machine:')
        if other_python_processes_ec2a == []:
            print('---')
        else:
            for i in other_python_processes_ec2a:
                print('\t',i)
        
        print('On EC2C Machine:')
        if other_python_processes_ec2c == []:
            print('---')
        else:
            for i in other_python_processes_ec2c:
                print('\t',i)
        print('On EC2D Machine:')
        if other_python_processes_ec2d == []:
            print('---')
        else:
            for i in other_python_processes_ec2d:
                print('\t',i)
        print('\n')   

    def show_machine_info_from_session(self):
        if is_running_on_ec2a():
            optics_datastore = get_optics_datastore_proximity()
            manager_process_list, manager_machine_name = self.get_optics_manager_details()
            # print (manager_process_list)
            for i in range(len(manager_process_list)):
                given_optics_spec_path = manager_process_list[i] 
                optics_spec_path = self.resolve_given_optics_spec_path(given_optics_spec_path)
                self.add_break_line()
                print(f'Machine status for {manager_process_list[i].split("/")[-1]}')
                self.add_break_line()
                optics_spec = OpticsSpec(optics_spec_path)
                dashboard = OpticsDashboard(optics_datastore,optics_spec)
                dashboard.show_session_details()
                print('\n')
        else:
            self.add_break_line()
            print('Machine status of spec files is only available on $OPTICS_DATASTORE machine. Please run this file on the $OPTICS_DATASTORE machine')
            self.add_break_line()
    def what_is_going_on(self):
        # Show manager processes
        self.show_manager_process_details()
        # Show test_runner processe
        self.show_test_runner_process_details()
        # Show other python processes
        self.show_other_python_processes()
        # Show disk space
        self.show_disk_space_details()
        # Show machine info from session
        self.show_machine_info_from_session()
        
if __name__ == '__main__':
    machine_name = None
    if is_running_on_ec2a():
        machine_name = 'ec2a'
    elif is_running_on_ec2c():
        machine_name = 'ec2c'
    elif is_running_on_ec2d():
        machine_name = 'ec2d'
    else: 
        machine_name = 'local'
    
    process_details = OpticsProcessDetails(machine_name)
    process_details.what_is_going_on()
   