import secrets
import string


def random_string(digits):
    alphabet = string.ascii_lowercase + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(digits))
    return password
