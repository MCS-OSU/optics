import time
#from scripts.machines import EC2B

STATUS_CHECKING_FOR_JOB   = 'status: checking_for_job every 5 seconds'


class ContainerJobScanner():
    def __init__(self, name, window, status_key):
        self.name = name
        self.window = window
        self.status_key = status_key

    def scan(self):
        while True:
            #container_to_run = self.check_for_job()
            # if not container_to_run == None:
            #     return container_to_run
            for i in range(7):
                self.window[self.status_key].update(STATUS_CHECKING_FOR_JOB + f' in {i} seconds')
                time.sleep(5)

    #def check_for_job(self):
        # ec2b = EC2B()
        # remote_src_path = '/home/ubuntu/eval6_systest/container_assignments.txt'
        # ec2b.get_file(remote_src_path, '.')
        # f = open('container_assignments.txt', 'r')
        # lines = f.readlines()
        # f.close()
        # assigned_container = None
        # for line in lines:
        #     if self.name in line:
        #         assigned_container = line.split(':')[0]
        # return assigned_container
