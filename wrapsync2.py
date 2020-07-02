#!/usr/bin/env python3

from os.path import dirname, isfile, realpath
import json
import subprocess
import sys

from utils import get_time, print_coloured

CONFIG_FILE_NAME = 'config.json'
SCRIPT_PARENT_DIR_PATH = dirname(realpath(sys.argv[0]))
CONFIG_FILE_PATH = f"{SCRIPT_PARENT_DIR_PATH}/{CONFIG_FILE_NAME}"


def main():
    """
    The application's main entry point.
    """
    args = parse_argv(sys.argv)
    config = get_config(CONFIG_FILE_PATH)
    cmd = get_rsync_command(config, args)
    cmd_string = ' '.join(cmd)

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        raise_error(f"Exception occurred while running the following command:\n{cmd_string}")
    except KeyboardInterrupt:
        print_coloured(f"[{get_time()}] ", 'white')
        print_coloured('KeyboardInterrupt: ', 'yellow', 'bold')
        print_coloured('User halted the execution\n', 'yellow')
        sys.exit(1)
    print_coloured(f"\n[{get_time()}] ", 'white')
    print_coloured('Synching finished. The following command has been executed:\n', 'green', 'bold')
    print_coloured(f"{cmd_string}\n", 'grey')


def parse_argv(argv=[]):
    """
    Validates and returns command-line arguments.
    @param argv: argument vector; all command-line arguments supplied to the script
    @return: a dictionary containing the 'action', 'dir_name' and any remaining arguments as 'options'
    """
    if len(argv) < 2:
        raise_error('No action has been specified in the first argument')
    action = argv[1]
    if action in ['help', '--help', '-help', '-h']:
        usage()
        sys.exit(0)
    if action not in ['push', 'pull']:
        raise_error('The action must either be \'push\' or \'pull\'')
    if len(argv) < 3:
        raise_error('No directory has been specified in the second argument')
    dir_name = argv[2]
    return {
        'action': action,
        'dir_name': dir_name,
        'options': argv[3:]
    }


def get_config(config_path):
    """
    Returns the config file contents as a dictionary or raises an error if the file doesn't exist.
    @param config_path: path to the config file
    @return: config file contents
    """
    if not isfile(config_path):
        raise_error(f"The config file doesn't exist in '{config_path}'")
    with open(config_path) as config_file:
        return json.load(config_file)


def get_paths(config, action, dir_name):
    """
    Returns 'from' and 'to' paths.
    @param config: wrapsync configuration
    @param action: 'push'/'pull'
    @param dir_name: name of the directory to append to paths from the config
    @return: dictionary containing 'from' and 'to' paths
    """
    paths = {
        'from': '',
        'to': ''
    }
    if action == 'push':
        if dir_name == 'all':
            paths['from'] = config['local-dir-path']
            # Parent dir of the remote dir
            paths['to'] = f"{config['username']}@{dirname(config['remote-dir-path'])}"
        else:
            paths['from'] = f"{config['local-dir-path']}/{dir_name}"
            paths['to'] = f"{config['username']}@{config['remote-dir-path']}"
    else:
        if dir_name == 'all':
            paths['from'] = f"{config['username']}@{config['remote-dir-path']}"
            # Parent dir of the local dir
            paths['to'] = dirname(config['local-dir-path'])
        else:
            paths['from'] = f"{config['username']}@{config['remote-dir-path']}/{dir_name}"
            paths['to'] = config['local-dir-path']
    return paths


def get_rsync_command(config, args):
    """
    Builds and returns the `rsync` command.
    @param config: the script's configuration
    @param args: command-line arguments
    @return: `rsync` command split into a list
    """
    cmd = ['rsync']
    # Append flags if, declared
    if config['flags']:
        cmd.append(f"-{config['flags']}")
    # Append exclusions, if declared
    if config['exclude']:
        for exclude in config['exclude']:
            cmd.append(f"--exclude='{exclude}'")
    # Append all remaining command-line arguments as rsync options
    for option in args['options']:
        cmd.append(option)
    # Append local and remote paths
    paths = get_paths(config, args['action'], args['dir_name'])
    cmd.append(paths['from'])
    cmd.append(paths['to'])
    return cmd


def raise_error(message):
    """
    Prints the given error message and exits with a non-zero code.
    @param message: error message
    """
    print_coloured(f"[{get_time()}] ", 'white')
    print_coloured('ERROR: ', 'red', 'bold')
    print_coloured(f"{message}\n\n", 'red')
    usage()
    sys.exit(1)


def usage():
    """
    Prints usage instructions.
    """
    print_coloured('Usage:\n', 'white', 'bold')
    print_coloured('$ ./wrapsync2.py ', 'white')
    print_coloured('<push/pull> <dir_name/all> [rsync_options]\n', 'yellow', 'bold')


if __name__ == '__main__':
    main()
