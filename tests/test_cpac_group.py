import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import PLATFORM_ARGS, TAGS


@pytest.mark.parametrize('args,platform', [
    (PLATFORM_ARGS[0], 'docker'),
    (PLATFORM_ARGS[1], 'singularity')
])
@pytest.mark.parametrize('tag', TAGS)
def test_utils_help(args, capsys, platform, tag):
    if tag is not None:
        args = args + f' --tag {tag}'
    argv = ['cpac', *args.split(' '), 'group', '--help']
    with mock.patch.object(sys, 'argv', [arg for arg in argv if len(arg)]):
        run()
        captured = capsys.readouterr()
        assert platform.title() in captured.out
        assert 'COMMAND' in captured.out
