FROM ubuntu as build
MAINTAINER Measurement Lab Support <support@measurementlab.net>
# Install the packages we need
RUN apt-get update && apt-get install -y git dh-autoreconf autoconf automake libtool gcc make libssl-dev libevent-dev libgeoip-dev paris-traceroute wget
WORKDIR /home/mk-pi/
RUN mkdir test-runner
RUN mkdir measurement-kit
ADD measurement-kit measurement-kit
WORKDIR measurement-kit
RUN ./autogen.sh && ./configure && make
RUN mv measurement_kit ../test-runner/
RUN mv GeoIP* ../test-runner/
WORKDIR /home/mk-pi/test-runner
ADD run.py . 

FROM arm64v8/alpine
RUN apk add --update python py-pip
RUN pip install pytz tzlocal
COPY --from=build /home/mk-pi/test-runner /test-runner
WORKDIR /test-runner
CMD ["python", "run.py"]
