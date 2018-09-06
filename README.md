# Murakami 
Murakami is a tool for creating an automatic Measurement Lab testing platform with as little effort as possible. Once running, Murakami runs an [NDT](https://www.measurementlab.net/tests/ndt/) test roughly every twelve hours and stores the results for your analysis.

## Setup
To get Murakami working, you'll need a few things:
1. A system on a chip computer. Murakami has been tested on [Raspberry Pi](https://www.raspberrypi.org/), but not yet on other systems. However, the docker image is compiled for the armv6 platform and should be widely compatible. Please let us know if you have success with other boards.
2. Whatever is needed to power your computer.
3. An ethernet cable. We recommend not testing over WiFi, as the limitations of the WiFi network may interfere with the test.
4. A case for your computer. This one is optional but probably a good idea.

## Installation
Murakami uses [docker](https://www.docker.com/) to make installation easier across as many different platforms as possible. You will need to install docker on your computer.
1. If you haven't already, install Raspbian using the [instructions on the website](https://www.raspberrypi.org/downloads/raspbian/) (if you're not planning on using the Raspberry Pi for anything else, you can choose the 'lite' version).
2. Install docker using [these instructions](https://docs.docker.com/install/linux/docker-ce/debian/#install-using-the-convenience-script) (don't try to install docker using `apt-get` as you will get a very old version).
3. Run the image:
```shell
$ mkdir data share
$ docker run -d --name mlab -v data:/data -v ~/share:/share --restart always measurementlab/murakami:1.0
```

## Statistics
Murakami will save a csv file in the `share` volume (which you can bind to any local directory through the command above) containing a row for each test run, with a timestamp, upload and download speed, and average round trip time (or 'ping'). Analysis for trends in the data can then be performed.
