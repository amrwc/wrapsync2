# w(r)ap(sync) 2

`wrapsync2` is a wrapper script for `rsync` and a Python rewrite of
[wrapsync][wrapsync]. Its main purpose is to simplify `rsync`'ing common
directories.

## Setup and usage

### Manual setup

1. Rename `config.example.json` to `config.json`.

1. Prepare the variables inside the config file.

   Required:

   - `username` – SSH login.
   - `domain` – full URL at which the SSH port is exposed.
   - `remote-path` – an absolute path to the remote directory containing
     everything we may want to sync.
   - `local-path` – an absolute path to the local directory containing
     everything we may want to sync.

   Optional:

   - `flags` – `rsync` flags; if no flags are given, this option will be
     omitted.
   - `exclude` – an array of patterns of file names/directory names; what
     matches these patterns will be excluded from syncing; defaults to no
     exclusions.

   Example config:

   - The SSH username is `georgesmith`.
   - The SSH URL is `ssh-example.com`.
   - The absolute path to the parent directory of all the directories/projects
     we may want to `rsync` on the remote machine is `/home/george/services`.
   - The local equivalent is `/Users/george/services`.
   - The `rsync` flags we need are `-a` and `-P`.
   - And George wants to exclude `node_modules` directory and all `*.jar` files
     from syncing.

   ```json
   "username": "georgesmith",
   "domain": "ssh-example.com",
   "remote-path": "/home/george/services",
   "local-path": "/Users/george/services",
   "flags": "aP",
   "exclude": ["node_modules", "*.jar"]
   ```

1. Run the script.

   ```console
   cd wrapsync2
   ./wrapsync2 <push/pull/help> <dir_name> [rsync_options]

   # Examples:
   ./wrapsync2 push my-first-python-project --update
   ./wrapsync2 pull my-second-python-project --delete
   ```

1. (Optional) For convenience, create a symlink to the script.

   ```console
   cd wrapsync2
   ln -s "$(pwd)/wrapsync2.py" /usr/local/bin/ws
   ```

   Now the script can be used from anywhere:

   ```console
   ws <pull/push/help> <dir_name> [options]

   # Examples:
   ws push linux --update
   ws pull windows --delete
   ```

### Unit tests

1. Install [Pytest][pytest].

   ```console
   pip3 install -U pytest
   ```

1. Run the tests.

   ```console
   python3 -m pytest

   # Or simply:
   pytest
   ```

### Linting

1. Install [Flake8][flake8].

   ```console
   pip3 install flake8
   ```

1. Run the linter manually.

   ```console
   flake8
   ```

1. Or, integrate the linter with the editor.

   VS Code-specific instructions:
   <https://code.visualstudio.com/docs/python/linting>

[flake8]: https://flake8.pycqa.org/en/latest/index.html
[pytest]: https://docs.pytest.org
[wrapsync]: https://github.com/amrwc/wrapsync
