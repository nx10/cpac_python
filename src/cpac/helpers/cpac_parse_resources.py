import os
import os.path as op
import requests
import uuid
import configparser
import traceback
import threading

from CPAC.info import __version__, ga_tracker


tracking_path = op.join(op.expanduser('~'), '.cpac')


def get_or_create_config():
    if not op.exists(tracking_path):
        parser = configparser.ConfigParser()
        parser.read_dict(dict(user=dict(uid=uuid.uuid1().hex,
                                        track=True)))
        with open(tracking_path, 'w') as fhandle:
            parser.write(fhandle)
    else:
        parser = configparser.ConfigParser()
        parser.read(tracking_path)

    return parser


def opt_out():
    parser = get_or_create_config()
    parser['user']['track'] = "False"
    with open(tracking_path, 'w') as fhandle:
        parser.write(fhandle)


def reset_uid():
    parser = get_or_create_config()
    parser.read_dict(dict(user=dict(uid=uuid.uuid1().hex,
                                    track=True)))
    with open(tracking_path, 'w') as fhandle:
        parser.write(fhandle)


def opt_in():
    if not get_uid():
        reset_uid()


def get_uid():
    parser = get_or_create_config()
    if parser['user'].getboolean('track'):
        uid = parser['user']['uid']
    else:
        uid = False
    return uid


def do_it(data, timeout):
    try:
        headers = { 'User-Agent': 'C-PAC 1.4.0' }
        response = requests.post('https://www.google-analytics.com/collect', data=data, timeout=timeout, headers=headers)
        return response
    except Exception as e:
        return False


def track_event(category, action, uid=None, label=None, value=0,
                software_version=None, timeout=2, thread=True):
    """
    Record an event with Google Analytics

    Parameters
    ----------
    tracking_id : str
        Google Analytics tracking ID.
    category : str
        Event category.
    action : str
        Event action.
    uid : str
        User unique ID, assigned when popylar was installed.
    label : str
        Event label.
    value : int
        Event value.
    software_version : str
        Records a version of the software.
    timeout : float
        Maximal duration (in seconds) for the network connection to track the
        event. After this duration has elapsed with no response (e.g., on a
        slow network connection), the tracking is dropped.
    """
    if uid is None:
        uid = get_uid()

    if not uid:
        return

    if os.environ.get('CPAC_TRACKING', '').lower() in ['0', 'false', 'off']:
        return

    this = "/CPAC/utils/ga.py"
    exec_stack = list(reversed(traceback.extract_stack()))
    assert exec_stack[0][0].endswith(this)
    package_path = exec_stack[0][0][:-len(this)]

    # only CPAC paths are going to be recorded
    file_path = ""
    for s in exec_stack:
        if s[0].endswith(this):
            continue
        if not s[0].startswith(package_path):
            break
        file_path = s[0][len(package_path):]

    data = {
        'v': '1',  # API version.
        'tid': ga_tracker,  # GA tracking ID
        'dp': file_path,
        'cid': uid,  # User unique ID, stored in `tracking_path`
        't': 'event',  # Event hit type.
        'ec': category,  # Event category.
        'ea': action,  # Event action.
        'el': label,  # Event label.
        'ev': value,  # Event value, must be an integer
        'aid': "CPAC",
        'an': "CPAC",
        'av': __version__,
        # 'aip': 1, # anonymize IP by removing last octet, slightly worse geolocation
    }
    
    if thread:
        t = threading.Thread(target=do_it, args=(data, timeout))
        t.start()
    else:
        do_it(data, timeout)


def track_run(level='participant', participants=0):
    assert level in ['participant', 'group']
    track_event('run', level, label='participants', value=participants, thread=False)