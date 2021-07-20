from django.dispatch import Signal

# Sent after successfully register with magic link email
post_magic_email_verified = Signal()

pre_user_deleted = Signal()
