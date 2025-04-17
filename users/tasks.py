from celery import shared_task
from datadex.models import SiteAsset
from utils.mail import send_html_email
from django.conf import settings


@shared_task
def send_welcome_email(user_email, username):
    assets = SiteAsset.objects.filter(
        name__in=['Logo', 'Banner']
    )

    print(f"Logo URL: {settings.BASE_URL}{assets.get(name='Logo').image.url}")
    print(f"Banner URL: {settings.BASE_URL}{assets.get(name='Banner').image.url}")

    send_html_email(
        subject="Welcome to Animatrixx!",
        to_email=user_email,
        template_name="emails/welcome_email.html",
        context={
            "username": username,
            "user": username,
            "logo_url": f"{settings.BASE_URL}{assets.get(name='Logo').image.url}",
            "banner_url": f"{settings.BASE_URL}{assets.get(name='Banner').image.url}",
        }
    )
