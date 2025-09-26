"""
This class represents a date as per RFC9110, to be used in HTTP headers.
"""

from datetime import datetime, timedelta, timezone

IMF_FIXDATE = "%a, %d %b %Y %X %Z"  # Sun, 06 Nov 1994 08:49:37 GMT
RFC850_DATE = "%A, %d-%b-%y %X %Z"  # Sunday, 06-Nov-94 08:49:37 GMT
ASCTIME_DATE = "%a %b %d %X %Y"     # Sun Nov  6 08:49:37 1994

class HttpDate:

    def __init__(self, date_str):
        parsed_date = self._parse_http_date(date_str)
        tz_unaware_iso_format = parsed_date.isoformat().split(".")[0]
        tz_aware_datetime = datetime.fromisoformat(tz_unaware_iso_format + "Z")
        self.date = tz_aware_datetime

    @staticmethod
    def _parse_http_date(date_str):
        """
        Parses the given date string according to RFC9110 HTTP date format. It supports obsolete formats as per RFC850,
        which are tested in order of preference. If none of the formats match, it will try to parse the date as a number
        which represents the number of seconds from the current time.

        :param date_str:
        :return:
        """

        try:
            return datetime.strptime(date_str, IMF_FIXDATE)
        except ValueError:
            pass

        try:
            dt = datetime.strptime(date_str, RFC850_DATE)
            delta = dt - datetime.now()
            if delta.days < 0 or abs(delta.days) >= 18250:
                raise RuntimeError("This is a date in the past")
            return dt
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, ASCTIME_DATE)
        except ValueError:
            pass

        try:
            return timedelta(seconds=int(date_str)) + datetime.now(timezone.utc)
        except ValueError:
            pass

        raise RuntimeError("This is definitely not a valid HTTP date")


    @property
    def is_future(self):
        return (self.date - datetime.now(timezone.utc)).total_seconds() > 0


    @property
    def diff_in_seconds(self):
        delta = self.date - datetime.now(timezone.utc)
        return abs(int(delta.total_seconds()))

