import datetime
import unittest

from outropy.copypasta.clock.clock import SystemClock


class TestSystemClock(unittest.TestCase):
    def test_returns_tz_naive_dates(self) -> None:
        self.assertIsNone(
            SystemClock.strptime("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S").tzinfo
        )
        self.assertIsNone(SystemClock.now_utc().tzinfo)
        self.assertIsNone(SystemClock.now_minus(1).tzinfo)
        self.assertIsNone(SystemClock.now_plus(1).tzinfo)
        self.assertIsNone(SystemClock.at(2023, 1, 1, 12, 0).tzinfo)
        self.assertIsNone(
            SystemClock.to_utc(datetime.datetime(2023, 1, 1, 12, 0)).tzinfo
        )
        self.assertIsNone(
            SystemClock.as_timezone_naive(datetime.datetime(2023, 1, 1, 12, 0)).tzinfo
        )
        self.assertIsNone(
            SystemClock.utc_begining_of_day_at(
                datetime.datetime(2023, 1, 1, 12, 0), "America/Los_Angeles"
            ).tzinfo
        )

    def test_utc_begining_of_day_at(self) -> None:
        date = SystemClock.at(2020, 1, 1, 12, 0, 0)
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "America/Los_Angeles"),
            SystemClock.as_timezone_naive(SystemClock.at(2020, 1, 1, 8, 0, 0)),
        )
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "America/New_York"),
            SystemClock.as_timezone_naive(SystemClock.at(2020, 1, 1, 5, 0, 0)),
        )
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "Europe/Berlin"),
            SystemClock.as_timezone_naive(SystemClock.at(2019, 12, 31, 23, 0)),
        )
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "Europe/Moscow"),
            SystemClock.as_timezone_naive(SystemClock.at(2019, 12, 31, 21, 0)),
        )
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "Asia/Kolkata"),
            SystemClock.as_timezone_naive(SystemClock.at(2019, 12, 31, 18, 30)),
        )
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "Asia/Shanghai"),
            SystemClock.as_timezone_naive(SystemClock.at(2019, 12, 31, 16, 0)),
        )
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "Australia/Sydney"),
            SystemClock.as_timezone_naive(SystemClock.at(2019, 12, 31, 13, 0)),
        )

    def test_at(self) -> None:
        dt = SystemClock.at(2023, 4, 6, 13, 23, 5)
        self.assertEqual(dt, datetime.datetime(2023, 4, 6, 13, 23, 5))
        self.assertIsNone(dt.tzinfo)

    def test_from_timestamp_utc(self) -> None:
        now = SystemClock.now_utc()
        ts = now.timestamp()
        self.assertEqual(SystemClock.from_timestamp_utc(ts), now)

    def test_isoformat(self) -> None:
        expectations = {
            "2023-04-06T13:23:05.000Z": datetime.datetime(2023, 4, 6, 13, 23, 5),
            "2023-11-23T20:54:28.119Z": datetime.datetime(
                2023, 11, 23, 20, 54, 28, 119000
            ),
            "2024-02-06T10:00:00": datetime.datetime(2024, 2, 6, 10, 0, 0),
            "2024-02-06T10:00:00-05:00": datetime.datetime(2024, 2, 6, 15, 0, 0),
            "2024-02-06T10:00:00+05:00": datetime.datetime(2024, 2, 6, 5, 0, 0),
            "2024-02-28T22:06:36Z": datetime.datetime(2024, 2, 28, 22, 6, 36),
        }

        for iso, expected in expectations.items():
            self.assertEqual(SystemClock.isoparse(iso), expected)

    def test_utc_begining_of_day_at_across_days(self) -> None:
        date = SystemClock.at(2020, 1, 2, 0, 1, 0)

        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "America/Los_Angeles"),
            SystemClock.as_timezone_naive(SystemClock.at(2020, 1, 1, 8, 0, 0)),
        )

        date = SystemClock.at(2020, 1, 2, 12, 0, 0)
        self.assertEqual(
            SystemClock.utc_begining_of_day_at(date, "Asia/Shanghai"),
            SystemClock.as_timezone_naive(SystemClock.at(2020, 1, 1, 16, 0, 0)),
        )
