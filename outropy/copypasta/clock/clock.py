import datetime
from contextlib import contextmanager
from typing import Generator, Optional
from zoneinfo import ZoneInfo

from dateutil import parser

from outropy.copypasta.exceptions import IllegalArgumentError


class Clock:
    def is_in_the_past(self, dt: datetime.datetime) -> bool:
        return self.now_utc() > dt

    def from_timestamp_utc(self, timestamp: float) -> datetime.datetime:
        return self.as_timezone_naive(datetime.datetime.fromtimestamp(timestamp))

    def strptime(self, datetime_as_string: str, format: str) -> datetime.datetime:
        return self.as_timezone_naive(
            datetime.datetime.strptime(datetime_as_string, format)
        )

    def now_utc(self) -> datetime.datetime:
        return self.as_timezone_naive(datetime.datetime.now(datetime.timezone.utc))

    def isoparse(self, datetime_as_string: str) -> datetime.datetime:
        try:
            return self.as_timezone_naive(parser.isoparse(datetime_as_string))
        except ValueError as e:
            raise IllegalArgumentError(
                f"Failed to parse datetime [{datetime_as_string}]"
            ) from e

    def maybe_isoparse(self, val: Optional[str]) -> Optional[datetime.datetime]:
        if val is None:
            return None
        return SystemClock.isoparse(val)

    def try_isoparse(self, val: Optional[str]) -> Optional[datetime.datetime]:
        if val is None:
            return None
        try:
            return self.isoparse(val)
        except IllegalArgumentError:
            return None

    def now_plus(
        self,
        days: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
        milliseconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        weeks: int = 0,
    ) -> datetime.datetime:
        delta = datetime.timedelta(
            days=days,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        )
        return self.now_utc() + delta

    def now_minus(
        self,
        days: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
        milliseconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        weeks: int = 0,
    ) -> datetime.datetime:
        delta = datetime.timedelta(
            days=days,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        )
        return self.now_utc() - delta

    def last_business_day(self) -> datetime.datetime:
        dt = self.now_utc()
        if dt.weekday() == 0:
            return dt - datetime.timedelta(days=3)
        if dt.weekday() == 6:
            return dt - datetime.timedelta(days=2)
        return dt - datetime.timedelta(days=1)

    def at(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microssecond: int = 0,
    ) -> datetime.datetime:
        return self.as_timezone_naive(
            datetime.datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                microssecond,
                tzinfo=datetime.timezone.utc,
            )
        )

    def to_utc(self, dt: datetime.datetime) -> datetime.datetime:
        return self.as_timezone_naive(dt.astimezone(datetime.timezone.utc))

    def as_timezone_naive(self, dt: datetime.datetime) -> datetime.datetime:
        if dt.tzinfo is not None:
            """
            If a datetime object has a timezone, calling replace will simplify drop that information and
            point it to the wrong time. For example 10:00-02:00 will become 10:00+00:00 and not 12:00+00:00

            Calling astimezone will perform the timezone conversion prior to droping tzinfo from the datetime object.

            Finally, it must be conditional as astimezone assumes that if tzinfo is None, it's local time.
            """
            dt = dt.astimezone(datetime.timezone.utc)
        dt = dt.replace(tzinfo=None)
        return dt

    def as_utc_timezone_aware(self, dt: datetime.datetime) -> datetime.datetime:
        if dt.tzinfo is None:
            """
            Same problem as `as_timezone_naive` but in reverse. If the datetime object is naive, it will be
            assumed to be local time and perform a conversion to UTC if we call astimezone on it.
            This is not what we want. All our naive dates are UTC.
            """
            return dt.replace(tzinfo=datetime.timezone.utc)
        else:
            return dt.astimezone(datetime.timezone.utc)

    def utc_begining_of_day_at(
        self, dt: datetime.datetime, timezone: str
    ) -> datetime.datetime:
        tz = ZoneInfo(timezone)
        # 1. make the date timezone aware
        dt = self.as_utc_timezone_aware(dt)

        # 2. shift the date to the desired timezone
        dt_shifted = dt.astimezone(tz)

        # 3. set the time to 00:00:00
        start = dt_shifted.replace(hour=0, minute=0, second=0, microsecond=0)

        # 4. shift the date back to naive
        return self.as_timezone_naive(start)


class FixedClock(Clock):
    def __init__(self, fixed_time: datetime.datetime) -> None:
        self.fixed_time = fixed_time

    def now_utc(self) -> datetime.datetime:
        return self.fixed_time


class DelegatingClock(Clock):
    def __init__(self, delegate: Clock) -> None:
        self.delegate = delegate

    def now_utc(self) -> datetime.datetime:
        return self.delegate.now_utc()


SystemClock = DelegatingClock(Clock())


@contextmanager
def fixed_clock(fixed_time: datetime.datetime) -> Generator[None, None, None]:
    global SystemClock
    clock = FixedClock(fixed_time)
    SystemClock.delegate = clock

    try:
        yield
    finally:
        SystemClock.delegate = Clock()
