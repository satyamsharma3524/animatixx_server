from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_html_email(
        subject, to_email, template_name, context={},
        from_email=None, plain_text=None):
    """
    Sends an HTML email with optional plain text fallback.

    Args:
        subject (str): Subject of the email.
        to_email (str or list): Recipient(s).
        template_name (str): Path to the HTML template.
        context (dict): Context for rendering the template.
        from_email (str): Sender email (defaults to DEFAULT_FROM_EMAIL).
        plain_text (str): Optional plain text fallback.
        If None, a default will be generated.
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    to_email = [to_email] if isinstance(to_email, str) else to_email

    html_content = render_to_string(template_name, context)
    text_content = plain_text or (
        f"Hi {context.get('user', '')}, "
        "view this email in a browser that supports HTML.")

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
