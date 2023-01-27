
import sys

def get_section_base_container():
    return ""


def get_section_ubuntu_configure():
    return ""


def get_section_opics_project_code(proj, repo, branch):
    return ""


def get_section_python_libs(proj, repo, branch):
    return ""


def get_section_numpy_hack(proj):
    return ""

if __name__ == '__main__':
    proj   = sys.argv[1]
    repo   = sys.argv[2]
    branch = sys.argv[3]

    section_base_container     = get_section_base_container()
    section_ubuntu_configure   = get_section_ubuntu_configure()
    section_opics_project_code = get_section_opics_project_code(proj, repo, branch)
    section_python_libs        = get_section_python_libs()
    section_numpy_hack         = get_section_numpy_hack(proj)

