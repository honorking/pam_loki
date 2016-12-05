
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.header import Header

SMTP_HOST = 'mx.hy01.wandoujia.com'
SMTP_PORT = 25


def sanitize_subject(subject):
    try:
        subject.decode('ascii')
    except UnicodeEncodeError:
        pass
    except UnicodeDecodeError:
        subject = Header(subject, 'utf-8')
    return subject


# Assuming send_mail() is intended for scripting usage, only Subject is sanitzed here.
# Also, the sanitzation procedure for other Headers is far too complicated.

def send_mail(subject=None, mail_from='ep-robots@wandoujia.com',
              mail_to=None, mail_cc=None, mail_body=None,
              mail_body_type='plain'):

    # Recipients check
    if not isinstance(mail_to, list):
        raise TypeError('Give me a list of mail_to')
    if mail_cc and not isinstance(mail_cc, list):
        raise TypeError('Give me a list of mail_cc')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = sanitize_subject(subject)
    msg['From'] = mail_from
    msg['To'] = ', '.join(mail_to)
    msg['Cc'] = ', '.join(mail_cc)
    body = MIMEText(mail_body, mail_body_type, 'utf-8')
    msg.attach(body)
    smtp = smtplib.SMTP()
    smtp.connect(SMTP_HOST, SMTP_PORT)
    smtp.sendmail(mail_from, mail_to, msg.as_string())
