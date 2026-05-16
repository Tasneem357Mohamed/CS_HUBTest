import os
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

# 1. Generate a unique filename for user uploads
def generate_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profiles', instance.user.username, unique_name)


# 2. Check if a user's subscription has expired
def is_subscription_active(profile):
    if not profile.expiry_date:
        return False
    # Check if expiry date is in the future
    return profile.expiry_date > timezone.now()


# 3. Get total order amount formatted as a string for receipts
def get_formatted_total(order):
    total = 0
    for item in order.items.all():
        total += item.price * item.quantity
    return f"${total:.2f}"


# 4. Deactivate users who haven't logged in for a year
def deactivate_inactive_users():
    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    inactive_users = User.objects.filter(last_login__lt=one_year_ago)
    
    for user in inactive_users:
        user.is_active = False
        user.save()
    
    return len(inactive_users)


# 5. Send an automated alert email to staff
def send_staff_alert(subject, message):
    staff_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=staff_emails,
        fail_silently=False,
    )
