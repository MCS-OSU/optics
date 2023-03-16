
import os, sys

from env.mcs_controller_init import McsControllerInitPvoe
from env.mcs_controller_init import McsControllerInitAvoe
from env.mcs_controller_init import McsControllerInitInter

def usage():
    print('usage:  python patch_controller_timeout.py pvoe|avoe|inter num_minutes')
if __name__ == '__main__':
   
    if len(sys.argv) < 3:
        usage()
        sys.exit()
        
    proj = sys.argv[1]
    if not proj in ['avoe','pvoe','inter']:
        print('project must be inter, pvoe, or avoe')
        usage()
        sys.exit()
        
    num_minutes = sys.argv[2]
    try:
        int_minutes = int(num_minutes)
    except Exception as err:
        print(err)
        print(f'...given num_minutes arg is not an int: {num_minutes}')
    
    if proj == 'avoe':
        mcs_init = McsControllerInitAvoe()
        mcs_init.patch_timeout(num_minutes)
    elif proj == 'inter':
        mcs_init = McsControllerInitInter()
        mcs_init.patch_timeout(num_minutes)
    elif proj == 'pvoe':
        mcs_init = McsControllerInitPvoe()
        mcs_init.patch_timeout(num_minutes)
        

        
    