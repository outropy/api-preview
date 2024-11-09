import datetime


def display_clock(dt: datetime.datetime) -> str:
    return dt.strftime("%H:%M")


def display_date(dt: datetime.datetime) -> str:
    return dt.strftime("%m/%d/%Y")
