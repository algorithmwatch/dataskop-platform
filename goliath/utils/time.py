import datetime


def date_within_margin(date: datetime.datetime, margin: datetime.timedelta):
    now = datetime.datetime.now()
    return now - margin <= date <= now + margin
