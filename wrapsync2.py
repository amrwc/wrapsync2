#!/usr/bin/env python3

import json
import os
import subprocess
import sys

from utils import get_time, print_coloured

ARGV = sys.argv

SCRIPT_PARENT_DIR_PATH = os.path.dirname(os.path.realpath(ARGV[0]))
CONFIG_FILE_NAME = 'config.json'
CONFIG_FILE_PATH = f"{SCRIPT_PARENT_DIR_PATH}/{CONFIG_FILE_NAME}"


def main():
    """
    The applications main entry point.
    """
    if not os.path.isfile(CONFIG_FILE_PATH):
        raise_error(
            f"The config file doesn't exist in '{CONFIG_FILE_PATH}'")
    with open(CONFIG_FILE_PATH) as config_file:
        config = json.load(config_file)

    if len(ARGV) < 2:
        raise_error('No action has been specified in the first argument')
    action = ARGV[1]
    if action in ['help', '--help', '-help', '-h']:
        usage()
        sys.exit(0)
    if action not in ['push', 'pull']:
        raise_error('The action must either be \'push\' or \'pull\'')
    if len(ARGV) < 3:
        raise_error('No directory has been specified in the second argument')
    dir_name = ARGV[2]

    # Define the `rsync` command
    cmd = ['rsync']
    # Append flags if any have been declared
    if config['flags']:
        cmd.append(f"-{config['flags']}")
    # Append excludions if any have been declared
    if config['exclude']:
        for exclude in config['exclude']:
            cmd.append(f"--exclude='{exclude}'")
    # Append any remaining command-line arguments as rsync options
    for option in ARGV[3:]:
        cmd.append(option)

    paths = get_paths(config, action, dir_name)
    cmd.append(paths['from'])
    cmd.append(paths['to'])

    cmd_string = ' '.join(cmd)
    try:
        subprocess.check_call(cmd)
    except:
        raise_error(
            f"Exception occurred while running the following command:\n{cmd_string}")
    print_coloured(f"[{get_time()}] ", 'white')
    print_coloured(
        f"\nSynching finished. The following command has been executed:\n", 'green', 'bold')
    print_coloured(f"{cmd_string}\n", 'grey')


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
            # Parent remote dir
            paths['to'] = f"{config['username']}@{os.path.dirname(config['remote-dir-path'])}"
        else:
            paths['from'] = f"{config['local-dir-path']}/{dir_name}"
            paths['to'] = f"{config['username']}@{config['remote-dir-path']}"
    else:
        if dir_name == 'all':
            paths['from'] = f"{config['username']}@{config['remote-dir-path']}"
            # Parent dir
            paths['to'] = os.path.dirname(config['local-dir-path'])
        else:
            paths['from'] = f"{config['username']}@{config['remote-dir-path']}/{dir_name}"
            paths['to'] = config['local-dir-path']
    return paths


def raise_error(message):
    """
    Prints the given error message and exits with a non-zero code.
    @param message: error message
    """
    print_coloured(f"[{get_time()}] ", 'white')
    print_coloured(f"ERROR: ", 'red', 'bold')
    print_coloured(f"{message}\n\n", 'red')
    usage()
    sys.exit(1)


def usage():
    """
    Prints usage instructions.
    """
    print_coloured('Usage:\n', 'white', 'bold')
    print_coloured('$ ./wrapsync2.py ', 'white')
    print_coloured(
        '<push/pull> <dir_name/all> [rsync_options]\n', 'yellow', 'bold')


if __name__ == '__main__':
    main()
