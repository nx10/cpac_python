import os
import pytest
import sys

from datetime import date

from cpac.__main__ import run
from CONSTANTS import SINGULARITY_OPTION
PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION]


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_help(args, capfd):
    sys.argv=['cpac', *args.split(' '), 'run', '--help']
    print(' '.join(sys.argv))
    run()
    captured = capfd.readouterr()
    assert 'participant' in captured.out or 'participant' in captured.err


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_test_config(args, capfd, tmp_path):
    wd = tmp_path
    sys.argv=(
        f'cpac {args} run '
        f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
        'test_config --participant_ndx=2'
    ).split(' ')
    run()
    captured = capfd.readouterr()
    assert(
        any([date.today().isoformat() in fp for fp in os.listdir(wd)])
    )


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_missing_data_config(args, capfd, tmp_path):
    wd = tmp_path
    sys.argv=(f'cpac {args} run {wd} {wd} test_config').split(' ')
    print(' '.join(sys.argv))
    run()
    captured = capfd.readouterr()
    assert('not empty' in '\n'.join([captured.err, captured.out]))