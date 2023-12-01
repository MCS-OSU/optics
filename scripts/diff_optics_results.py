import os, sys

from core.optics_spec_loader           import OpticsSpec
from optics_results.optics_scores      import OpticsScores

def resolve_given_optics_spec_path(given_path):
    if given_path.startswith('/'):
        return given_path
    return os.path.join(os.getcwd(), given_path)

def is_valid_spec_path(p):
    if not os.path.isfile(p):
        return False
    if not p.endswith('.cfg'):
        return False
    f = open(p, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if 'controller:mcs' in line:
            return True
    return False
 
def usage():
    print("\nusage:  python optics_results_diff.py  totals|details <spec_path_1> <spec_path_2>\n")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
        sys.exit()

    scope = sys.argv[1]
    if scope not in ['totals','details']:
        print(f"\nscope (first parameter) must be either 'totals' or 'details'")
        usage()
        sys.exit()

    spec_path_1 = resolve_given_optics_spec_path(sys.argv[2])
    if not is_valid_spec_path(spec_path_1):
        print(f'\nspec_path_1 {spec_path_1} not found')
        usage()
        sys.exit()

    spec_path_2 = resolve_given_optics_spec_path(sys.argv[3])
    if not is_valid_spec_path(spec_path_2):
        print(f'\nspec_path_2 {spec_path_2} not found')
        usage()
        sys.exit()
        
    print(f'spec_path_1: {spec_path_1}')
    print(f'spec_path_2: {spec_path_2}')

    optics_spec_1 = OpticsSpec(spec_path_1)
    proj1 = optics_spec_1.proj

    optics_spec_2 = OpticsSpec(spec_path_2)
    proj2 = optics_spec_2.proj

    if not proj1 == proj2:
        print(f'projects for these specs are different: {proj1} vs {proj2} - cannot meaningfully compare')
        sys.exit()

    optics_scores_1 = OpticsScores(proj1,optics_spec_1)
    optics_scores_2 = OpticsScores(proj1,optics_spec_2)

    print(f'\n\n              -  difference {scope} -\n\n')

    if scope == 'totals':
        optics_scores_1.show_totals_diff(optics_scores_2)
    elif scope == 'details':
        optics_scores_1.show_details_diff(optics_scores_2)
    else:
        pass