'''
    module for easy interface to smtplib for sending emails
'''
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(server_adress, server_port, cred_login, cred_pw, sender_email, receiver_email, subject, content):
    '''
        function for sending an email. authentication is performed on server_adress:server_port,
        with authentication being cred_login, cred_pw. target email is receiver_email, message
        content of mail.
    '''
    init_res = init_ssl_server(server_adress, server_port, cred_login, cred_pw)
    if init_res['success']:
        message = create_mime_message(sender_email, receiver_email, subject, content)
        init_res["server"].sendmail(sender_email, receiver_email, message.as_string())
    else:
        print("error authenticating to smtp server. returned exeception is:")
        print(init_res["except"])


def init_ssl_server(server_adress, server_port, cred_login, cred_pw):
    '''
        Initialize conntection to ssl server on server_adress:server_port using cred_login and
        cred_pw for autehntication. returns dict with "success" noting if initalization was
        successfull. if successfull the "server" key contains the successfull initalized stmp server
        object.
    '''
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(server_adress, server_port)
        server.starttls(context=context)
        server.ehlo()
        server.login(cred_login, cred_pw)
        return {"success": True, "server": server}
    except Exception as e:
        return {"success": False, "except" : e}

def create_mime_message(_from, _to, subject, content):
    '''
        Create a mime_message object with from, to, subject and content given by param
    '''
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = _from
    message["To"] = _to
    text = MIMEText(content,"plain")
    message.attach(text)
    return message