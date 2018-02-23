FROM arm32v6/alpine as build
MAINTAINER Measurement Lab Support <support@measurementlab.net>
# Install the packages we need
RUN apk add --update build-base linux-headers git autoconf automake libtool gcc make libressl-dev libevent-dev geoip geoip-dev wget
WORKDIR /home/mk-pi/
RUN mkdir test-runner
RUN mkdir measurement-kit
ADD measurement-kit measurement-kit
WORKDIR measurement-kit
RUN /home/mk-pi/measurement-kit/autogen.sh
RUN /home/mk-pi/measurement-kit/configure --disable-shared
RUN make
RUN mv measurement_kit ../test-runner/
RUN mv GeoIP* ../test-runner/
WORKDIR /home/mk-pi/test-runner
ADD run.py . 
CMD python run.py

FROM arm32v6/alpine
RUN apk add --update libstdc++ python py-pip libressl libevent geoip ca-certificates
RUN update-ca-certificates
RUN pip install pytz tzlocal
COPY --from=build /home/mk-pi/test-runner /test-runner
WORKDIR /test-runner
CMD python run.py
