import pytest
import subprocess
from unittest.mock import patch, mock_open

from wrapsync2 import (
    parse_argv,
    get_config,
    get_paths,
    build_remote_path,
    build_local_path,
    get_rsync_command,
    build_exclude_option,
    execute_rsync,
    main
)

USERNAME = 'johndoe'
DOMAIN = 'example.com'
LOCAL_PATH = 'local/dir/path'
LOCAL_PARENT_PATH = 'local/dir'
REMOTE_PATH = 'remote/dir/path'
REMOTE_PARENT_PATH = 'remote/dir'
CONFIG = {
    'username': USERNAME,
    'domain': DOMAIN,
    'local-path': LOCAL_PATH,
    'remote-path': REMOTE_PATH,
    'flags': 'aP',
    'exclude': ["node_modules", "*.jar"]
}


@pytest.mark.parametrize('argv', [
    ([]),  # Not enough arguments
    (['script_name.py']),  # Not enough arguments
    (['script_name.py', 'act']),  # Wrong action
    (['script_name.py', 'push'])  # No directory specified
])
def should_have_raised_error_while_parsing_argv_for_incorrect_input(argv):
    with pytest.raises(SystemExit) as e:
        parse_argv(argv)
    assert e.type == SystemExit
    assert e.value.code == 1


@pytest.mark.parametrize('argv', [(['script_name.py', 'help']), (['script_name.py', 'HeLp'])])
def should_have_displayed_usage_information_while_parsing_argv(argv):
    with pytest.raises(SystemExit) as e:
        parse_argv(argv)
    assert e.type == SystemExit
    assert e.value.code == 0


@pytest.mark.parametrize('argv, expected_result', [
    (['script_name.py', 'push', 'directory_name', '--update', '--another-option'],
        {'action': 'push', 'dir_name': 'directory_name', 'options': ['--update', '--another-option']}),
    (['script_name.py', 'pull', 'directory_name'],
        {'action': 'pull', 'dir_name': 'directory_name', 'options': []})
])
def should_have_gotten_argv(argv, expected_result):
    assert parse_argv(argv) == expected_result


def should_have_raised_error_while_getting_config_when_the_file_doesnt_exist(monkeypatch):
    monkeypatch.setattr('wrapsync2.isfile', lambda *args, **kwargs: False)
    with pytest.raises(SystemExit) as e:
        get_config('config.json')
    assert e.type == SystemExit
    assert e.value.code == 1


def should_have_gotten_config(monkeypatch):
    config = {'test-key': 'test-val'}
    monkeypatch.setattr('wrapsync2.isfile', lambda *args, **kwargs: True)
    with patch('builtins.open', mock_open(read_data='data')):
        monkeypatch.setattr('wrapsync2.json.load', lambda *args, **kwargs: config)
        assert get_config('random-config.json') == config


@pytest.mark.parametrize('action, dir_name, expected_result', [
    ('push', 'all', {'from': LOCAL_PATH, 'to': f"{USERNAME}@{DOMAIN}:{REMOTE_PARENT_PATH}"}),
    ('pull', 'all', {'from': f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}", 'to': LOCAL_PARENT_PATH}),
    ('push', 'SomeDir', {'from': f"{LOCAL_PATH}/SomeDir", 'to': f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}"}),
    ('pull', 'SomeDir', {'from': f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}/SomeDir", 'to': LOCAL_PATH})
])
def should_have_gotten_paths(action, dir_name, expected_result):
    assert get_paths(CONFIG, action, dir_name) == expected_result


@pytest.mark.parametrize('is_parent, expected_result', [
    (True, f"{USERNAME}@{DOMAIN}:{REMOTE_PARENT_PATH}"),
    (False, f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}")
])
def should_have_built_remote_path(is_parent, expected_result):
    assert build_remote_path(CONFIG, is_parent) == expected_result


@pytest.mark.parametrize('is_parent, expected_result', [
    (True, LOCAL_PARENT_PATH),
    (False, LOCAL_PATH)
])
def should_have_built_local_path(is_parent, expected_result):
    assert build_local_path(CONFIG, is_parent) == expected_result


@pytest.mark.parametrize('args, expected_result', [
    ({'action': 'push', 'dir_name': 'directory_name', 'options': []},
     ['rsync', '-aP', '--exclude={\'node_modules\',\'*.jar\'}',
      f"{LOCAL_PATH}/directory_name", f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}"]),
    ({'action': 'pull', 'dir_name': 'directory_name', 'options': []},
     ['rsync', '-aP', '--exclude={\'node_modules\',\'*.jar\'}',
      f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}/directory_name", f"{LOCAL_PATH}"]),
    ({'action': 'push', 'dir_name': 'all', 'options': ['--update']},
     ['rsync', '-aP', '--exclude={\'node_modules\',\'*.jar\'}',
      '--update', f"{LOCAL_PATH}", f"{USERNAME}@{DOMAIN}:{REMOTE_PARENT_PATH}"]),
    ({'action': 'pull', 'dir_name': 'all', 'options': ['--delete', '--whatever']},
     ['rsync', '-aP', '--exclude={\'node_modules\',\'*.jar\'}',
      '--delete', '--whatever', f"{USERNAME}@{DOMAIN}:{REMOTE_PATH}", f"{LOCAL_PARENT_PATH}"])
])
def should_have_gotten_rsync_command(args, expected_result):
    assert get_rsync_command(args, CONFIG) == expected_result


@pytest.mark.parametrize('excludes, expected_result', [
    ([], '--exclude={}'),
    (['node_modules'], '--exclude={\'node_modules\'}'),
    (['node_modules', '*.jar'], '--exclude={\'node_modules\',\'*.jar\'}')
])
def should_have_build_exclude_option(excludes, expected_result):
    assert build_exclude_option(excludes) == expected_result


@pytest.mark.parametrize('exception', [(subprocess.CalledProcessError), (KeyboardInterrupt)])
def should_have_handled_exception_while_executing_rsync(monkeypatch, exception):
    def mock_check_call(*args, **kwargs):
        raise exception('', '')
    monkeypatch.setattr('wrapsync2.subprocess.check_call', mock_check_call)
    with pytest.raises(SystemExit) as e:
        execute_rsync([])
    assert e.type == SystemExit
    assert e.value.code == 1


def should_have_executed_rsync(monkeypatch):
    try:
        monkeypatch.setattr('wrapsync2.subprocess.check_call', lambda *args, **kwargs: None)
        execute_rsync([])
    except Exception:
        pytest.fail('Should have executed rsync')


def should_have_executed_all_required_components_via_main(monkeypatch):
    monkeypatch.setattr('wrapsync2.parse_argv', lambda *args, **kwargs:
                        {'action': 'push', 'dir_name': 'dir', 'options': []})
    monkeypatch.setattr('wrapsync2.get_config', lambda *args, **kwargs: CONFIG)
    monkeypatch.setattr('wrapsync2.subprocess.check_call', lambda *args, **kwargs: None)
    try:
        main()
    except Exception:
        pytest.fail('Should have executed all required components via main')
