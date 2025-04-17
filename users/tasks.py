from celery import shared_task
from utils.mail import send_html_email


@shared_task
def send_welcome_email(user_email, username):
    send_html_email(
        subject="Welcome to Animatrixx!",
        to_email=user_email,
        template_name="emails/welcome_email.html",
        context={"username": username, "user": username}
    )
