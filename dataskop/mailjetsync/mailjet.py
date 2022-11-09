"""
Subscribe an email address as confirmed email address to a mailjet list.

The property name `dataskop_tiktok_2022_donated` is hard-coded. Adapt it for further usage.
"""

import json

from django.conf import settings
from mailjet_rest import Client

API_KEY = settings.ANYMAIL["MAILJET_API_KEY"]
API_SECRET = settings.ANYMAIL["MAILJET_SECRET_KEY"]
mailjet_list_id = settings.MAILJET_SUBSCRIBE_LIST_ID

mailjet = Client(auth=(API_KEY, API_SECRET))


def subscribe_mailjet_list(email, donated=False):
    """
    `donated` is not verified and could be tempered with. We can't verify it, because
    the newsletter email address and the email address for the donation can differ.
    """
    data = {
        "Properties": {"dataskop_tiktok_2022_donated": donated},
        # Add to the list even though the contact has previusly unsubscribed from the list
        "Action": "addforce",
        "Email": email,
    }
    # The endpoints creates a new contact if needed
    result = mailjet.contactslist_managecontact.create(id=mailjet_list_id, data=data)
    if result.status_code != 201:
        raise ValueError(
            f"API with wrong response: {result.status_code} {result.json()}"
        )


def get_contact_meta():
    result = mailjet.contactmetadata.get()
    print(result.status_code)
    print(json.dumps(result.json(), indent=2))


def create_contact_meta():
    data = {
        "Datatype": "bool",
        "Name": "dataskop_tiktok_2022_donated",
        "NameSpace": "static",
    }
    result = mailjet.contactmetadata.create(data=data)
    print(result.status_code)
    print(json.dumps(result.json(), indent=2))
