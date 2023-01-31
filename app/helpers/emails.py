"""
Helper file to send mails
for different purposes
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def signup_notification_email(username, email):
    """
    helper function to notify
    facet-superadmin that a new user has
    signed up to the system
    """
    sender_email = current_app.config["MAIL_USERNAME"]
    password = current_app.config["MAIL_PASSWORD"]
    reciever_email = current_app.config["MAIL_USERNAME"]
    message = f"""\
    Subject: New User Sign-Up Notification

    
    Dear Superadmin,

    A new user has signed up on the system. Please find the details below:

    Name: {username}
    Email: {email}

    Please take the necessary actions to verify the new user and activate their account.

    Thank you,
    """

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email,
            reciever_email,
            message
        )
    return "email sent successfully"
