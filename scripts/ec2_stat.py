from scripts.ec2.machines import EC2A, EC2C

from core.utils import notify_mcs_optics_status

if __name__=='__main__':
    ec2a = EC2A()
    ec2a.show_running_scenes()
    ec2a.show_disk_space()

    ec2c = EC2C()
    ec2c.show_running_scenes()
    ec2c.show_disk_space()
    #notify_mcs_optics_status('machine status checked')