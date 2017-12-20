import datetime
import json
import logging
import os
import random
import re
import subprocess
import time
import tempfile
import shutil
import urllib2
import json
import csv

import pytz
import tzlocal

def format_time(utc_time):
    utc_time_explicit = utc_time.replace(tzinfo=pytz.utc)
    localized = utc_time_explicit.astimezone(tzlocal.get_localzone())
    localized = localized.replace(microsecond=0)
    return localized.strftime('%Y-%m-%dT%H:%M:%S%z')
    
def do_ndt_test():
    now = int(subprocess.check_output(["date", "-u", "+%s"]))
    result_raw = subprocess.check_output(["measurement_kit", "--reportfile=/data/ndt-%d.njson"%now, "ndt"])
    return result_raw

def summarize_tests():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile: # Location of shared volume between docker containers
        historywriter = csv.writer(tmpfile)
        historywriter.writerow(["Datetime", "Download", "Upload"])
        for file in os.listdir("/data"):
            with open("/data/" + file) as json_data:
                d = json.load(json_data)
                historywriter.writerow([d["measurement_start_time"], d["test_keys"]["simple"]["download"], d["test_keys"]["simple"]["upload"]])
        tmp_loc = tmpfile.name
        tmpfile.close()
        logging.info("Copying temp file from %s", tmp_loc)
        shutil.copy(tmp_loc, "/share/history.csv")

def perform_test_loop(expected_sleep_secs=24*60*60):
    while True:
        try:
            ndt_result = do_ndt_test()
        except subprocess.CalledProcessError as ex:
            logging.error('Error in NDT test: %s', ex)
        summarize_tests()
        sleeptime = random.expovariate(1.0/expected_sleep_secs)
        resume_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=sleeptime)
        logging.info('Sleeping for %u seconds (until %s)', sleeptime, resume_time)
        time.sleep(sleeptime)

if __name__ == "__main__":
    root_log = logging.getLogger()
    root_log.setLevel(logging.INFO)
    perform_test_loop()
