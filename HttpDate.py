"""
This class represents a date as per RFC9110, to be used in HTTP headers.
"""

from datetime import datetime, timedelta

IMF_FIXDATE = "%a, %d %b %Y %X %Z"  # Sun, 06 Nov 1994 08:49:37 GMT
RFC850_DATE = "%A, %d-%b-%y %X %Z"  # Sunday, 06-Nov-94 08:49:37 GMT
ASCTIME_DATE = "%a %b %d %X %Y"     # Sun Nov  6 08:49:37 1994

class HttpDate:

    def __init__(self, date_str):
        self.date = self._parse_http_date(date_str)

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
            return datetime.strptime(date_str, RFC850_DATE)
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, ASCTIME_DATE)
        except ValueError:
            pass

        try:
            return timedelta(seconds=int(date_str)) + datetime.now()
        except ValueError:
            pass

        raise RuntimeError("This is definitely not a valid HTTP date")


    @property
    def is_future(self):
        return self.diff_in_seconds > 0


    @property
    def diff_in_seconds(self):
        return int((datetime.now() - self.date).total_seconds())

