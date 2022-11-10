from django.dispatch import Signal

# Sent after successfully login in (e.g. first time confirming the email address)
post_magic_login = Signal()

pre_user_deleted = Signal()
