import datetime
import json
import logging
import os
import random
import re
import subprocess
import time
import urllib2
import json
import csv

import pytz
import tzlocal

def setup_logger():
    logger = logging.getLogger('pyNDT')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    file_handler = logging.FileHandler('pyndt.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

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
    with open("/share/history.csv", "wb") as historyfile: # Location of shared volume between docker containers
        historywriter = csv.writer(historyfile)
        historywriter.writerow(["Datetime", "Download", "Upload"])
        for file in os.listdir("/data"):
            with open("/data/" + file) as json_data:
                d = json.load(json_data)
                historywriter.writerow([d["measurement_start_time"], d["test_keys"]["simple"]["download"], d["test_keys"]["simple"]["upload"]])



def perform_test_loop():
    while True:
        try:
            ndt_result = do_ndt_test()
        except Exception as ex:
            logger.error('Error in NDT test: %s', ex)
        summarize_tests()
        sleeptime = random.expovariate(1.0/43200.0)
        resume_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=sleeptime)
        logger.info('Sleeping for %u seconds (until %s)', sleeptime, resume_time)
        time.sleep(sleeptime)

if __name__ == "__main__":
    perform_test_loop()
