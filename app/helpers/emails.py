"""
Helper file to send mails
for different purposes
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from jinja2 import Environment
import logging
from .email_contents import forgot_password_mail_content

def signup_notification_email(email_data):
    """
    helper function to notify
    facet-superadmin or org_admin that a new user has
    signed up to the system/ organization
    """
    try:
        message = f"""\
        Dear Superadmin,

        A new user has signed up on the system. Please find the details below:

        Name: {email_data['username']}
        Email: {email_data['email']}
        Organization : {email_data['organization']}

        Please take the necessary actions to verify the new user and activate their account.

        Thank you,
        """
        logging.info("Mail request for signup notification to superadmin for user:%s of organization:%s",email_data['email'],email_data['organization'])
        msg = EmailMessage()
        msg['Subject'] = "New User Sign-Up Notification"
        msg['To'] = email_data["reciever_email"]
        msg['From'] = email_data["sender_mail"]
        msg.set_content(message)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_data["sender_mail"], email_data["password"])
            server.send_message(msg)
            logging.info("Mail request sucessfull for signup notification to superadmin for user:%s of organization:%s",email_data['email'],email_data['organization'])
    except Exception as err:
        logging.exception("Failed to send email for signup notification updates due to the following error:%s",err)


def project_notifications(email_data, email_type):
    """
    Notification function for notifying
    user if they have been removed or added to the project
    """
    try:
        project_name = email_data["project"]
        project_status = (
            f"Added to project {project_name}"
            if email_type == 1
            else f"Removed from project {project_name}"
        )
        message = f"""\
        Dear User,

        You have been {project_status} by project admin: {email_data['project_admin']}
        
        Thank you
        """
        logging.info("Mail request for project updates to email_id:%s and for project:%s",email_data['reciever_email'],project_name)
        msg = EmailMessage()
        msg['Subject'] = "Project Updates"
        msg['To'] = email_data["reciever_email"]
        msg['From'] = email_data["sender_email"]
        msg.set_content(message)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_data["sender_email"], email_data["password"])
            server.send_message(msg)
            logging.info("Mail sent successfully for project updates to email_id:%s and for project:%s",email_data['reciever_email'],project_name)
    except Exception as err:
        logging.exception("Failed to send email for project updates due to the following error:%s",err)

def forgot_password_mail(email_data):
    """
    Email function for sending url to user in case of
    forgot password
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Forgot Password"
        message["From"] = email_data['sender_email']
        message["To"] = email_data['reciever_email']
        # html content recieved
        html_content = forgot_password_mail_content
        part1 = MIMEText(
            Environment()
            .from_string(html_content)
            .render(
                reset_password_url = email_data['reset_password_url']
            ),
            "html",
        )
        message.attach(part1)
        fp = open('media/images/logo.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image1>')
        message.attach(msgImage)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_data["sender_email"], email_data["password"])
            server.sendmail(
                        email_data["sender_email"],
                        email_data['reciever_email'],
                        message.as_string(),
                    )
            logging.info("Mail sent successfully for forgot password to email_id:%s",email_data['reciever_email'])
    except Exception as err:
        logging.exception("Failed to send email for forgot password due to the following error:%s",err)
    