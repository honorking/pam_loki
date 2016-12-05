'''Log user activity for future auditing'''

import os
import json
from socket import gethostname
from datetime import datetime
from .mail import send_mail


def read_config():
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'auditing.json'
    )
    with open(config_file, 'rt') as f:
        config_dict = json.load(f)
    return config_dict


def do_send(user, service, message):
    subject_tpl = 'Failed login attemps from {}'
    body_tpl = '''
    One failed login attempt has been detected.
    Host: {host}
    Service: {service}
    User: {user}
    Time: {time}
    Info: {info}
    '''
    config_dict = read_config()
    mail_to = config_dict.get('mail_to', None)
    mail_cc = config_dict.get('mail_cc', None)
    # Not sending mails if no recipients are given.
    if not mail_to:
        return None

    body_dict = {
        'host': gethostname(),
        'service': service,
        'user': user,
        'time': str(datetime.now()),
        'info': message
    }
    subject = subject_tpl.format(gethostname())
    body = body_tpl.format(**body_dict)
    send_mail(subject=subject, mail_to=mail_to, mail_cc=mail_cc, mail_body=body)
