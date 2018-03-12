#!/usr/bin/env python
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

   
def do_ndt_test(country_code=""):
    """Runs the NDT test as a subprocess and returns the raw results.

    Args:
       `country_code`: A capitalized, two-letter country code representing the location of
           the desired test server. If no country code is supplied, the script uses the default mlab_ns
           behavior.
    Returns:
       The STDOUT of the call to `measurement_kit`.
    """
    now = int(subprocess.check_output(["date", "-u", "+%s"]))
    if country_code == "": # If there is a country code, use it, otherwise default
        # We are using the `-g` flag due to a regex stack overflow segmentation fault bug in GNU's C++ library
        # Measurement-kit issue #1276: https://github.com/measurement-kit/measurement-kit/issues/1276
        result_raw = subprocess.check_output(["/test-runner/measurement_kit", "-g",
            "--reportfile=/data/ndt-%d.njson"%now, "ndt"])
    else:
        result_raw = subprocess.check_output(["/test-runner/measurement_kit", "-g",
            "--reportfile=/data/ndt-%d.njson"%now, "ndt", "-C", country_code])
    return result_raw

def summarize_tests():
    """Converts measurement_kit .njson test results into a single .csv file.

    This function checks the `/data/` directory for all files, reads the json into an object and writes
    the object into a csv file that it stores in `/share/history.csv` (the `share` directory is shared
    between this Docker image and the dashboard image).
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile: 
        historywriter = csv.writer(tmpfile)
        historywriter.writerow(["Datetime", "Download", "Upload"])
        for file in os.listdir("/data"):
            with open("/data/" + file) as json_data:
                d = json.load(json_data)
                historywriter.writerow([d["measurement_start_time"], d["test_keys"]["simple"]["download"],
                    d["test_keys"]["simple"]["upload"],
                    d["test_keys"]["simple"]["ping"]])
        tmp_loc = tmpfile.name
        tmpfile.close()
        logging.info("Copying temp file from %s", tmp_loc)
        shutil.copy(tmp_loc, "/share/history.csv")

def perform_test_loop(expected_sleep_secs=12*60*60):
    """The main loop of the script.
    
    It gathers the computer's location, then loops forever calling measurement_kit twice each time, once with
    the default mlab_ns behavior and once setting the computer's country code as the `country` policy. It
    then sleeps for a random interval (determined by an exponential distribution) that will average out to
    expected_sleep_seconds.

    Args:
        `expected_sleep_seconds`: The desired average time, in seconds, between tests.
    """
    # Get location by IP for country specific test
    # Example taken from https://stackoverflow.com/questions/11787941/get-physical-position-of-device-with-python
    f = urllib2.urlopen('http://freegeoip.net/json')
    json_string = f.read()
    f.close()
    location = json.loads(json_string)
    while True:
        # Run the test twice, once with the default mlab_ns responder
        # and once explicitly with the `country` policy set to the 
        # endpoint's country as determined above by freegeoip.net.
        try:
            ndt_result = do_ndt_test("")
        except subprocess.CalledProcessError as ex:
            logging.error('Error in NDT test: %s', ex)
        try:
            ndt_result = do_ndt_test(location['country_code'])
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
