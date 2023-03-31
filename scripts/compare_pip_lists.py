import sys, os
from env.pip_list_comparer import PipListComparer
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python compare_pip_lists.py avoe|inter|pvoe')
        sys.exit()

    if sys.argv[1] not in ['avoe','inter','pvoe']:
        print('usage: python compare_pip_lists.py avoe|inter|pvoe')
        sys.exit()

    if 'OPTICS_HOME' not in os.environ:
        print('ERROR - OPTICS_HOME not defined.  Please "export OPTICS_HOME=<root of optics repo pull>"')
        sys.exit()


    comparer = PipListComparer()
    comparer.compare(sys.argv[1])