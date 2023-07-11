import os

ec2d = 'ubuntu@52.72.153.236'
pem = '/home/ubuntu/main_optics/scripts/ec2/shared-with-opics.pem'

def tfer(proj, dir):
    os.chdir('/home/ubuntu/eval6_systest/' + proj)
    os.system(f'zip -r {proj}_{dir}.zip {dir}')
    target_dir = f'/home/ubuntu/eval6_systest/{proj}'
    os.system(f'scp -i {pem} {proj}_{dir}.zip {ec2d}:{target_dir}')
    os.system(f'ssh -i {pem} {ec2d} "cd /home/ubuntu/eval6_systest/{proj};unzip {proj}_{dir}.zip;rm {proj}_{dir}.zip"')
    os.system(f'rm {proj}_{dir}.zip')

if __name__ == '__main__':
    #tfer('pvoe','scenes')
    # tfer('pvoe','test_sets')
    # tfer('pvoe','versions')
    # tfer('inter','scenes')
    # tfer('inter','test_sets')
    # tfer('inter','versions')
    # tfer('avoe','test_sets')
    # tfer('avoe','versions')

    tfer('avoe','scenes')
    # adding a comment to push and test a git command

    
    
    
