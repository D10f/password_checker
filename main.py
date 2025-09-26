#!/usr/bin/env python3

import os
import sys
import time

from client import HTTPClient

VERSION = "0.0.0"

DEFAULT_HEADERS = {
    "Add-Padding": "false",
    "Connection": "keep-alive",
    "User-Agent": f"{os.path.basename(__file__)}/{VERSION}",
}


def main():

    # with HTTPClient("api.pwnedpasswords.com", 80) as client:
    with HTTPClient("haveibeenpwned.com", 80) as client:

        client.set_headers(DEFAULT_HEADERS)

        response = client.get("/")
        print(response.text)

        # print(
        #     response.request.path,
        #     response.http_version,
        #     response.status_code,
        #     response.status_reason,
        #     response.text,
        #     response.headers
        # )

        # response = client.get("/")
        # print(
        #     response.request.path,
        #     response.http_version,
        #     response.status_code,
        #     response.status_reason,
        # )
        #
        # time.sleep(1)
        #
        # if client.is_connected():
        #     response = client.get("/50x.html")
        #     print(
        #         response.request.path,
        #         response.http_version,
        #         response.status_code,
        #         response.status_reason,
        #     )
        #
        # time.sleep(1)
        #
        # if client.is_connected():
        #     response = client.get("/redirect?amount=150000000&format=rfc850")
        #     print(
        #         response.request.path,
        #         response.http_version,
        #         response.status_code,
        #         response.status_reason,
        #     )

    return 0


if __name__ == "__main__":
    sys.exit(main())
