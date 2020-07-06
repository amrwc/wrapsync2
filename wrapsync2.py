#!/usr/bin/env python3

"""
`wrapsync2` is a wrapper script for `rsync` and a Python rewrite of [wrapsync][wrapsync]. Its main purpose is to
simplify `rsync`'ing common directories.

`rsync` works with files and directories alike. The key to correctly synchronise is to recognise that the source is
directly transported into the destination. I.e. when a directory is specified as a source and a directory with the same
name is the destination, it will get 'duplicated'. E.g.:

```
# Bad, not intuitive copy
rsync john@ssh-example.com:/home/john/my-app /home/john/my-app
```

The above will create a copy of the remote `my-app` directory inside of the local path, resulting in
`/home/john/my-app/my-app`. To avoid such case and, more intuitively, overwrite/update the `my-app` directory, the
parent directory must be supplied. I.e.:

```
# Good, will overwrite/update the local copy
rsync john@ssh-example.com:/home/john/my-app /home/john

# Analogously, overwrite/update the remote copy
rsync /home/john/my-app john@ssh-example.com:/home/john
```

@author amrwc
"""

from os.path import dirname, isfile, realpath
import json
import subprocess
import sys

from utils import raise_error, usage, print_cmd, get_time, print_coloured

CONFIG_FILE_NAME = 'config.json'
SCRIPT_PARENT_DIR_PATH = dirname(realpath(sys.argv[0]))
CONFIG_FILE_PATH = f"{SCRIPT_PARENT_DIR_PATH}/{CONFIG_FILE_NAME}"


def main():
    """
    The application's entry point.
    """
    args = parse_argv(sys.argv)
    config = get_config(CONFIG_FILE_PATH)
    cmd = get_rsync_command(args, config)
    execute_rsync(cmd)


def parse_argv(argv=[]):
    """
    Validates and returns command-line arguments.
    @param argv: argument vector; all command-line arguments supplied to the script
    @return: a dictionary containing the 'action', 'dir_name' and any remaining arguments as 'options'
    """
    if len(argv) < 2:
        raise_error('No action has been specified in the first argument')
    action = argv[1]
    if action.lower() in ['--help', '-help', '-h', 'help']:
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
    path_from = ''
    path_to = ''
    if action == 'push':
        if dir_name == 'all':
            path_from = build_local_path(config, False)
            path_to = build_remote_path(config, True)
        else:
            path_from = f"{build_local_path(config, False)}/{dir_name}"
            path_to = build_remote_path(config, False)
    else:
        if dir_name == 'all':
            path_from = build_remote_path(config, False)
            path_to = build_local_path(config, True)
        else:
            path_from = f"{build_remote_path(config, False)}/{dir_name}"
            path_to = build_local_path(config, False)
    return {
        'from': path_from,
        'to': path_to
    }


def build_remote_path(config, is_parent):
    """
    Builds and returns the remote path based on the given config. If `is_parent` is `True`, returns the parent
    directory.
    @param config: wrapsync configuration
    @param is_parent: whether the path should point to the parent directory of what's in the config
    @return: built remote path
    """
    remote_path = dirname(config['remote-path']) if is_parent else config['remote-path']
    return f"{config['username']}@{config['domain']}:{remote_path}"


def build_local_path(config, is_parent):
    """
    Builds and returns the local path based on the given config. If `is_parent` is `True`, returns the parent
    directory.
    @param config: wrapsync configuration
    @param is_parent: whether the path should point to the parent directory of what's in the config
    @return: built local path
    """
    return dirname(config['local-path']) if is_parent else config['local-path']


def get_rsync_command(args, config):
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
    # Append exclusions
    cmd.append(build_exclude_option(config['exclude']))
    # Append all remaining command-line arguments as rsync options
    for option in args['options']:
        cmd.append(option)
    # Append local and remote paths
    paths = get_paths(config, args['action'], args['dir_name'])
    cmd.append(paths['from'])
    cmd.append(paths['to'])
    return cmd


def build_exclude_option(excludes):
    """
    Builds and returns the `--exclude` rsync option.
    @param excludes: list of patterns to exclude
    @return: `--exclude` option
    """
    exclude_option = '--exclude={'
    for i, exclude in enumerate(excludes):
        exclude_option += ',' if i > 0 else ''
        exclude_option += f"'{exclude}'"
    exclude_option += '}'
    return exclude_option


def execute_rsync(cmd):
    """
    Executes the given `rsync` command as a sub-process.
    @param cmd: pre-built rsync command split into a list
    """
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        raise_error('Exception occurred while running the following command:', cmd)
    except KeyboardInterrupt:
        print_coloured(f"\n[{get_time()}] ", 'white')
        print_coloured('KeyboardInterrupt: ', 'yellow', 'bold')
        print_coloured('User halted the execution of the following command:\n', 'yellow')
        print_cmd(cmd)
        sys.exit(1)
    print_coloured(f"\n[{get_time()}] ", 'white')
    print_coloured('Synching finished. The following command has been executed:\n', 'green', 'bold')
    print_cmd(cmd)


if __name__ == '__main__':
    main()
