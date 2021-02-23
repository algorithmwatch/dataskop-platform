Setup emails for mailjet

```Python
from mailjet_rest import Client

api_key = ""
api_secret = ""

mailjet = Client(auth=(api_key, api_secret))

# don't specify email for first parse route

data = {"Email": "random@random.org", "Url": "https://user:password@unding.de/anymail/mailjet/inbound/"}

result = mailjet.parseroute.create(data=data)

# update already created

# result = mailjet.parseroute.update(id="random@random.org",data=data)

print(result.status_code)
print(result.json())
```
