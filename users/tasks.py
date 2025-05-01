from celery import shared_task
from datadex.models import WebsiteAsset
from utils.mail import send_html_email


@shared_task
def send_welcome_email(user_email, username):
    assets = WebsiteAsset.objects.filter(
        asset_type__in=["logo", "banner"],
        name__in=["logo", "banner"]
    )
    asset_map = {
        asset.name.lower(): asset.image.url for asset in assets if asset.image}

    context = {
        "username": username,
        "user": username,
        "logo_url": asset_map.get("logo"),
        "banner_url": asset_map.get("banner"),
    }

    send_html_email(
        subject="Welcome to Animatrixx!",
        to_email=user_email,
        template_name="emails/welcome_email.html",
        context=context
    )
