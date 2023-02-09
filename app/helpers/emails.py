"""
Helper file to send mails
for different purposes
"""
import smtplib
import ssl

# username, email, sender_email, password, reciever_email, organization


def signup_notification_email(email_data):
    """
    helper function to notify
    facet-superadmin or org_admin that a new user has
    signed up to the system/ organization
    """
    message = f"""\
    Subject: New User Sign-Up Notification

    
    Dear Superadmin,

    A new user has signed up on the system. Please find the details below:

    Name: {email_data['username']}
    Email: {email_data['email']}
    Organization : {email_data['organization']}

    Please take the necessary actions to verify the new user and activate their account.

    Thank you,
    """

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_data["sender_mail"], email_data["password"])
        server.sendmail(
            email_data["sender_mail"], email_data["reciever_email"], message
        )


def project_notifications(email_data, email_type):
    """
    Notification function for notifying
    user if they have been removed or added to the project
    """
    project_name = email_data["project"]
    project_status = (
        f"Added to project {project_name}"
        if email_type == 1
        else f"Removed from project {project_name}"
    )
    message = f"""\
    Subject: Project Updates


    Dear User,

    You have been {project_status} by project admin: {email_data['project_admin']}
    Thank you
    """

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_data["sender_email"], email_data["password"])
        server.sendmail(
            email_data["sender_email"], email_data["reciever_email"], message
        )
