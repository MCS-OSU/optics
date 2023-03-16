
import os, sys

from env.mcs_controller_init import McsControllerInitPvoe
from env.mcs_controller_init import McsControllerInitAvoe
from env.mcs_controller_init import McsControllerInitInter

def usage():
    print('usage:  python patch_controller_timeout.py pvoe|avoe|inter num_seconds')
if __name__ == '__main__':
   
    if len(sys.argv) < 3:
        usage()
        sys.exit()
        
    proj = sys.argv[1]
    if not proj in ['avoe','pvoe','inter']:
        print('project must be inter, pvoe, or avoe')
        usage()
        sys.exit()
        
    num_seconds = sys.argv[2]
    try:
        int_seconds = int(num_seconds)
    except Exception as err:
        print(err)
        print(f'...given num_seconds arg is not an int: {num_seconds}')
    
    if proj == 'avoe':
        mcs_init = McsControllerInitAvoe()
        mcs_init.patch_timeout(num_seconds)
    elif proj == 'inter':
        mcs_init = McsControllerInitInter()
        mcs_init.patch_timeout(num_seconds)
    elif proj == 'pvoe':
        mcs_init = McsControllerInitPvoe()
        mcs_init.patch_timeout(num_seconds)
        

        
    