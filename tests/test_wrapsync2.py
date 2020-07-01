import pytest

from wrapsync2 import parse_argv, get_paths, get_rsync_command

USERNAME = 'johndoe'
LOCAL_DIR_PATH = 'local/dir/path'
LOCAL_PARENT_DIR_PATH = 'local/dir'
REMOTE_DIR_PATH = 'remote/dir/path'
REMOTE_PARENT_DIR_PATH = 'remote/dir'
CONFIG = {
    'username': USERNAME,
    'local-dir-path': LOCAL_DIR_PATH,
    'remote-dir-path': REMOTE_DIR_PATH,
    'flags': 'aP',
    'exclude': ["node_modules", "*.jar"]
}


@pytest.mark.parametrize('argv, expected_result', [
    (['script_name.py', 'push', 'directory_name', '--update', '--another-option'],
        {'action': 'push', 'dir_name': 'directory_name', 'options': ['--update', '--another-option']}),
    (['script_name.py', 'pull', 'directory_name'],
        {'action': 'pull', 'dir_name': 'directory_name', 'options': []})
])
def test_should_have_gotten_command_line_arguments(argv, expected_result):
    assert(parse_argv(argv)) == expected_result


@pytest.mark.parametrize('action, dir_name, expected_result', [
    ('push', 'all', {'from': LOCAL_DIR_PATH, 'to': f"{USERNAME}@{REMOTE_PARENT_DIR_PATH}"}),
    ('pull', 'all', {'from': f"{USERNAME}@{REMOTE_DIR_PATH}", 'to': LOCAL_PARENT_DIR_PATH}),
    ('push', 'SomeDir', {'from': f"{LOCAL_DIR_PATH}/SomeDir", 'to': f"{USERNAME}@{REMOTE_DIR_PATH}"}),
    ('pull', 'SomeDir', {'from': f"{USERNAME}@{REMOTE_DIR_PATH}/SomeDir", 'to': LOCAL_DIR_PATH})
])
def test_should_have_gotten_correct_paths(action, dir_name, expected_result):
    assert(get_paths(CONFIG, action, dir_name)) == expected_result


@pytest.mark.parametrize('args, expected_result', [
    ({'action': 'push', 'dir_name': 'directory_name', 'options': []},
     ['rsync', '-aP', '--exclude=\'node_modules\'', '--exclude=\'*.jar\'',
      f"{LOCAL_DIR_PATH}/directory_name", f"{USERNAME}@{REMOTE_DIR_PATH}"]),
    ({'action': 'pull', 'dir_name': 'directory_name', 'options': []},
     ['rsync', '-aP', '--exclude=\'node_modules\'', '--exclude=\'*.jar\'',
      f"{USERNAME}@{REMOTE_DIR_PATH}/directory_name", f"{LOCAL_DIR_PATH}"]),
    ({'action': 'push', 'dir_name': 'all', 'options': ['--update']},
     ['rsync', '-aP', '--exclude=\'node_modules\'', '--exclude=\'*.jar\'',
      '--update', f"{LOCAL_DIR_PATH}", f"{USERNAME}@{REMOTE_PARENT_DIR_PATH}"]),
    ({'action': 'pull', 'dir_name': 'all', 'options': ['--delete', '--whatever']},
     ['rsync', '-aP', '--exclude=\'node_modules\'', '--exclude=\'*.jar\'',
      '--delete', '--whatever', f"{USERNAME}@{REMOTE_DIR_PATH}", f"{LOCAL_PARENT_DIR_PATH}"])
])
def test_should_have_gotten_correct_rsync_command(args, expected_result):
    assert(get_rsync_command(CONFIG, args)) == expected_result
