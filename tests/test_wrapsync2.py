from wrapsync2 import get_paths

username = 'johndoe'
local_dir_path = 'local/dir/path'
local_parent_dir_path = 'local/dir'
remote_dir_path = 'remote/dir/path'
remote_parent_dir_path = 'remote/dir'
config = {
    'username': username,
    'local-dir-path': local_dir_path,
    'remote-dir-path': remote_dir_path
}


def test_should_have_gotten_correct_path_when_syncing_all_directories():
    assert(get_paths(config, 'push', 'all')) == {
        'from': local_dir_path,
        'to': f"{username}@{remote_parent_dir_path}"
    }
    assert(get_paths(config, 'pull', 'all')) == {
        'from': f"{username}@{remote_dir_path}",
        'to': local_parent_dir_path
    }


def test_should_have_gotten_correct_path_when_syncing_specified_directories():
    dir_name = 'SomeDirName'
    assert(get_paths(config, 'push', dir_name)) == {
        'from': f"{local_dir_path}/{dir_name}",
        'to': f"{username}@{remote_dir_path}"
    }
    assert(get_paths(config, 'pull', dir_name)) == {
        'from': f"{username}@{remote_dir_path}/{dir_name}",
        'to': local_dir_path
    }
