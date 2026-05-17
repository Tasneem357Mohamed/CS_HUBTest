import os
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

def generate_profile_path(instance, filename):
    """
    Generate a unique filename for user uploads.
    
    Args:
        instance (object): The instance of the model.
        filename (str): The original filename.
    
    Returns:
        str: The unique filename.
    """
    if not filename:
        raise ValueError("Filename is required")
    ext = filename.split('.')[-1]
    if not ext:
        raise ValueError("File extension is required")
    unique_name = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profiles', instance.user.username, unique_name)

def is_subscription_active(profile):
    """
    Check if a user's subscription has expired.
    
    Args:
        profile (object): The user's profile.
    
    Returns:
        bool: True if the subscription is active, False otherwise.
    
    Raises:
        ValueError: If the expiry date is not provided.
    """
    if not profile.expiry_date:
        raise ValueError("Expiry date is required")
    return profile.expiry_date > timezone.now()

def get_formatted_total(order):
    """
    Calculate the total order amount and format it as a string.
    
    Args:
        order (object): The order object.
    
    Returns:
        str: The formatted total amount.
    
    Raises:
        ValueError: If the order object does not have an items attribute.
    """
    if not hasattr(order, 'items'):
        raise ValueError("Order object must have an items attribute")
    total = 0
    for item in order.items.all():
        total += item.price * item.quantity
    return f"${total:.2f}"

def deactivate_inactive_users():
    """
    Deactivate users who haven't logged in for a year.
    
    Returns:
        int: The number of deactivated users.
    """
    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    inactive_users = User.objects.filter(last_login__lt=one_year_ago)
    for user in inactive_users:
        if user.last_login:
            user.is_active = False
            user.save()
    return len(inactive_users)

def send_staff_alert(subject, message):
    """
    Send an automated alert email to staff.
    
    Args:
        subject (str): The email subject.
        message (str): The email message.
    
    Returns:
        None
    """
    staff_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=staff_emails,
            fail_silently=False,
        )
    except Exception as e:
        # Handle email sending failure
        print(f"Error sending email: {e}")