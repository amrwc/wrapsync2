# w(r)ap(sync) 2

`wrapsync2` is a wrapper script for `rsync` and a Python rewrite of
[wrapsync][wrapsync]. Its main purpose is to simplify `rsync`'ing common
directories.

## Setup and usage

### Manual setup

1. Rename `config.example.json` to `config.json`.

1. Prepare the variables inside of the `config.json` file.

   Required:

   - `username` – SSH login,
   - `remote-dir-path` – an absolute path to the remote directory containing
     everything we may want to sync, e.g. `john@ssh-example.com:/home/john/services`,
   - `local-dir-path` – an absolute path to the local directory containing
     everything we may want to sync, e.g. `/Users/Documents/services`.

   Optional:

   - `flags` – `rsync` flags; if no flags are given, this option will be
     omitted,
   - `exclude` – an array of patterns of file names/directory names; what
     matches these patterns will be excluded from synchronising; defaults to no
     exclusions; e.g.:

     ```json
     "exclude": [
       "node_modules",
       "vendor",
       "bin",
       "*.class"
     ]
     ```

1. Create a symlink to the script for convenience.

   ```console
   cd wrapsync2
   ln -s "$(pwd)/wrapsync2.py" /usr/local/bin/ws
   ```

1. Now the script can be used from anywhere:

   ```console
   ws <pull/push> <service> [options]

   # Examples:
   ws push linux --update
   ws pull windows --delete
   ```

### Unit tests

1. Install [Pytest][pytest].

   ```console
   pip install -U pytest
   ```

1. Run the tests.

   ```console
   python3 -m pytest
   # Or simply...
   pytest
   ```

[pytest]: https://docs.pytest.org
[wrapsync]: https://github.com/amrwc/wrapsync
