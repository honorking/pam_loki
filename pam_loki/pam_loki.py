#!/usr/bin/env python2

import json
import syslog
import time
from pwd import getpwnam
from functools import partial
from socket import gethostname
from urllib2 import urlopen
from urllib2 import Request
from urllib2 import URLError, HTTPError

# LOKI_URL = 'http://loki-test.hy01.internal.wandoujia.com/api/privilege/authorize'
LOKI_URL = 'http://loki.hy01.internal.wandoujia.com/api/privilege/authorize'
RETRY_TIMES = 3
RETRY_INTERVAL = 1
REQUEST_TIMEOUT = 3
PAM_SERVICE_MAP = {
    'sshd': 'login',
    'sudo': 'work',
    'sudo-i': 'work',
}


# ----- auth -----
def pam_sm_authenticate(pamh, flags, argv):
    return pamh.PAM_IGNORE


def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_IGNORE


# ----- account -----
def pam_sm_acct_mgmt(pamh, flags, argv):
    username = pamh.ruser if pamh.ruser else pamh.get_user()
    try:
        uid = getpwnam(username)[2]
    except KeyError:
        _audit(username, pamh.service, False, 'Could not get uid for user `{0}` '.format(username))
        return pamh.PAM_SYSTEM_ERR
    hostname = gethostname()
    privilege_type = 'server'
    # Map PAM service name to Loki priviledge name
    try:
        privilege_name = PAM_SERVICE_MAP[pamh.service]
    except KeyError:
        _audit(username, pamh.service, False, '`{0}` service not available'.format(pamh.service))
        return pamh.PAM_SYSTEM_ERR

    success_msg = '{0}/{1}: Account opened for {2}@{3}.'.format(
        privilege_type, privilege_name, username, hostname
    )
    failed_msg = ''

    if uid < 3000:
        # Direct pass system users
        is_auth_success = True
    else:
        is_auth_success = None
        retry_count = 0
        while retry_count < RETRY_TIMES:
            try:
                _check_loki(username, hostname, privilege_type, privilege_name)
            except AuthDenied as e:
                is_auth_success = False
                failed_msg = str(e)
                break
            except ServerError as e:
                # Retry in next loop
                failed_msg = str(e)
                retry_count += 1
                time.sleep(RETRY_INTERVAL)
                continue
            else:
                is_auth_success = True
                break

    if is_auth_success is None:
        # This means after max retries server still can't accomplish the
        # authorization process, pass the authorization directly
        is_auth_success = True
        extra_msg = 'skip authorization after max retries'
        _audit(username, pamh.service, False, extra_msg)
        success_msg += ' (' + extra_msg + ')'

    if is_auth_success:
        _audit(username, pamh.service, True, 'acct_mgmt success')
        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, success_msg))
        return pamh.PAM_SUCCESS
    else:
        _audit(username, pamh.service, False, e)
        pamh.conversation(pamh.Message(pamh.PAM_ERROR_MSG, failed_msg))
        return pamh.PAM_PERM_DENIED


# ----- session -----
def pam_sm_open_session(pamh, flags, argv):
    username = pamh.ruser if pamh.ruser else pamh.get_user()
    _audit(username, pamh.service, True, 'open_session success')
    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    username = pamh.ruser if pamh.ruser else pamh.get_user()
    _audit(username, pamh.service, True, 'close_session success')
    return pamh.PAM_SUCCESS


# ----- password -----
def pam_sm_chauthtok(pamh, flags, argv):
    return pamh.PAM_IGNORE


class AuthDenied(Exception):
    """Authorization denied by server"""


class ServerError(Exception):
    """Server error when request loki api"""


def _check_loki(username, hostname, privilege_type, privilege_name):
    post_data = {
        'username': username,
        'hostname': hostname,
        'privilege_type': privilege_type,
        'privilege_name': privilege_name
    }
    headers = {
        'Content-Type': 'application/json'
    }
    req = Request(LOKI_URL, json.dumps(post_data), headers)
    try:
        urlopen(req, timeout=REQUEST_TIMEOUT)
    except HTTPError as e:
        if e.code >= 500:
            raise ServerError(str(e))

        if e.code == 400:
            msg = 'Invalid parameter. Please report this to sre-team@wandoujia.com: {0}'.format(e.read())
        elif e.code == 401:
            msg = 'Authorization denied. You need `{0}` privilege for this server'.format(privilege_name)
        else:
            msg = 'Authorization denied. Reason: {0}'.format(e.read())
        raise AuthDenied(msg)
    except URLError as e:
        raise ServerError(str(e))


def _audit(user=None, service=None, successful=None, message=''):

    syslog.openlog("pam_loki.py", syslog.LOG_PID, syslog.LOG_AUTH)
    info = partial(syslog.syslog, syslog.LOG_INFO)
    err = partial(syslog.syslog, syslog.LOG_ERR)

    log_tpl = 'USER={0}, SERVICE={1}, MESSAGE={2}'

    if successful:
        info(log_tpl.format(user, service, message))
    else:
        err(log_tpl.format(user, service, message))
