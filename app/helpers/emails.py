"""
Helper file to send mails
for different purposes
"""
import smtplib
import ssl

def signup_notification_email(username, email, sender_email, password):
    """
    helper function to notify
    facet-superadmin that a new user has
    signed up to the system
    """
    sender_email = sender_email
    password = password
    reciever_email = sender_email
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
        server.sendmail(sender_email, reciever_email, message)
