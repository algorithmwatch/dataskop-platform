# Security

# Authenficiation

Users are only allowed to login via email (magic link).
This prevents password leak access but we still have to block brute force attacks.

Magic links can only be opened from the same IP address where the user requested the magic link.
This may be problem if you only have email on your smartphone but want to login on the desktop.

## Sessions

We store sessions with Redis and the session cookie is only valid for 1 day.
