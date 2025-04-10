from csv import writer as csv_writer
from hashlib import md5
from pandas import Timestamp
from pprint import pp
from requests import get as http_get
from time import sleep, gmtime, strftime
import os
from requests.exceptions import RequestException

DATAFEED_HOMEPAGE = "https://api.secondlife.com/datafeeds/homepage.txt"
DATASAMPLE_HOMEPAGE = """\
signups_updated_slt
2025-04-03 09:02:18
signups_updated_unix
1743696138
signups
68482461
exchange_rate_updated_slt
2025-04-03 09:22:58
exchange_rate_updated_unix
1743697378
exchange_rate
255.22
inworld_updated_unix
1743697980
inworld_updated_slt
2025-04-03 09:33:00
inworld
35666
"""

DATAFEED_LINDEX = "https://api.secondlife.com/datafeeds/lindex.txt"
DATASAMPLE_LINDEX = """\
updated_unix
1743732485
updated_slt
2025-04-03 19:08:05
ll_1h_min_rate
263
ll_1h_max_rate
263
ll_1h_l$
8000.00
ll_1h_us$
30.42
ll_1d_min_rate
252
ll_1d_max_rate
267
ll_1d_l$
297800.00
ll_1d_us$
1126.42
ll_t_min_rate
252
ll_t_max_rate
266
ll_t_l$
97800.00
ll_t_us$
376.58
mb_1h_min_rate
253
mb_1h_max_rate
255
mb_1h_l$
3755278.00
mb_1h_us$
14827.58
mb_1d_min_rate
252
mb_1d_max_rate
266
mb_1d_l$
69527167.00
mb_1d_us$
275256.73
mb_t_min_rate
252
mb_t_max_rate
266
mb_t_l$
56718818.00
mb_t_us$
224554.40
lb_10%_l$_offer
29545406.00
lb_10%_min_rate
261
lb_10%_max_rate
287
ms_1h_min_rate
263
ms_1h_max_rate
263
ms_1h_l$
318184.00
ms_1h_us$
1209.84
ms_1d_min_rate
255
ms_1d_max_rate
268
ms_1d_l$
12713097.00
ms_1d_us$
48077.13
ms_t_min_rate
255
ms_t_max_rate
268
ms_t_l$
10578953.00
ms_t_us$
40028.01
ls_10%_l$_offer
982329872.00
ls_10%_min_rate
229
ls_10%_max_rate
254
exchange_rate_updated_unix
1743732485
exchange_rate_updated_slt
2025-04-03 19:08:05
exchange_rate
254.39
"""

DIR_DATA = "data/"
DIR_DATA_HOMEPAGE = "data/homepage/"
DIR_DATA_LINDEX = "data/lindex/"

if not os.path.exists(DIR_DATA):
    os.mkdir(DIR_DATA)

if not os.path.exists(DIR_DATA_HOMEPAGE):
    os.mkdir(DIR_DATA_HOMEPAGE)

if not os.path.exists(DIR_DATA_LINDEX):
    os.mkdir(DIR_DATA_LINDEX)

REQUEST_TIMEOUT = 60
REQUEST_RATE = "2 min"


def call_api():
    now = Timestamp.now()
    next = now.ceil(REQUEST_RATE)
    print(
        f"> woke at {now.strftime("%H:%M:%S")}, "
        f"waiting until {next.strftime("%H:%M:%S")}"
    )
    pause_until(next.timestamp())

    while True:
        try:
            r = http_get(DATAFEED_HOMEPAGE, timeout=REQUEST_TIMEOUT)
            digest, data = multiline_to_kvp(r.text)
            write_homepage_data(data, digest, gmtime())
            print(r.status_code, r.headers["content-type"])
            pp(data)

            r = http_get(DATAFEED_LINDEX, timeout=REQUEST_TIMEOUT)
            digest, data = multiline_to_kvp(r.text)
            write_lindex_data(data, digest, gmtime())
            print(r.status_code, r.headers["content-type"])
            pp(data)
        except RequestException as e:
            print("> HTTP request failed:", e)

        next = Timestamp.now().ceil(REQUEST_RATE).timestamp()
        pause_until(next)


def multiline_to_kvp(text):
    digest = md5(text.encode()).hexdigest()
    text = text.splitlines()
    data = dict(zip(text[0::2], text[1::2]))
    return (digest, data)


def write_homepage_data(data, digest, now):

    fname = f"{strftime("%Y-%m-%d-%H-%M", now)}-{digest}"
    with open(DIR_DATA_HOMEPAGE + f"{fname}.csv", "w+", newline="") as file:
        csv = csv_writer(file)
        csv.writerow(["Key", "Value"])
        for key, value in data.items():
            csv.writerow([key, value])


def write_lindex_data(data, digest, now):

    fname = f"{strftime("%Y-%m-%d-%H-%M", now)}-{digest}"
    with open(DIR_DATA_LINDEX + f"{fname}.csv", "w+", newline="") as file:
        csv = csv_writer(file)
        csv.writerow(["Key", "Value"])
        for key, value in data.items():
            csv.writerow([key, value])


def pause_until(tstamp: int | float):
    """
    Inspired by Python Pause
    """
    if not isinstance(tstamp, (int, float)):
        raise Exception("The time parameter is not a number")

    while True:
        now = Timestamp.now().timestamp()
        if tstamp <= now:  # caller is waiting for the past
            break  # or enough time has passed

        remaining = tstamp - now
        wait = remaining * 0.90
        if wait < 1:  # Don't wanna spam too much
            wait = 1  # and it's okay to overshoot

        print("nap %.1fs ..." % wait)
        sleep(wait)


call_api()
