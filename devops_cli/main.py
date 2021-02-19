""" Main entrypoint """
import sys
from .utils import eprint


def main():
    """ Main entrypoint, will hand off to other modules for it's actual work """
    if len(sys.argv) < 3:
        eprint('devops-cli [module] [command] <args>')
        sys.exit(1)
    module_name = sys.argv[1]
    func_name = sys.argv[2].replace('-', '_')
    module = __import__(f"devops_cli.{module_name}", fromlist=[func_name])
    try:
        sys.exit(getattr(module, func_name)(sys.argv[3:]))
    except AttributeError as e:
        eprint(e)
        eprint(f"devops-cli {module_name} has no function named {sys.argv[2]}")
        sys.exit(1)


if __name__ == '__main__':
    main()
