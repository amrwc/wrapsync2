import pytest

from utils import raise_error


@pytest.mark.parametrize('message, cmd', [('msg', ['cmd']), ('msg', None)])
def should_have_raised_error(message, cmd):
    with pytest.raises(SystemExit) as e:
        raise_error('Any message')
    assert e.type == SystemExit
    assert e.value.code == 1
