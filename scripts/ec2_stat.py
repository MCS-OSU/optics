from scripts.ec2.machines import EC2A, EC2B

from scripts.optics.core.utils import notify_mcs_optics_status

if __name__=='__main__':

    ec2b = EC2B()
    ec2b.show_running_scenes()
    ec2b.show_disk_space()

    ec2a = EC2A()
    ec2a.show_running_scenes()
    ec2a.show_disk_space()

    notify_mcs_optics_status('machine status checked')