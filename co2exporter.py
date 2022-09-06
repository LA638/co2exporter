#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Prometheus http:8057 exporter for CO₂/temperature monitoring with USB CO₂ monitor

from sys import stdout
from time import sleep
from co2meter import CO2monitor
from prometheus_client import Gauge, start_http_server


EXPORTER_PORT = 8057
REQUEST_DELAY = 10
AVG_COUNT = 6


# Creating metrics
MONITOR_REQUEST_DURATION_SECONDS = Gauge('monitor_request_duration_seconds', 
                                         'USB CO2 Monitor Request Duration')
TEMPERATURE_C = Gauge('temperature_c', 
                      'Current Temperature, C')
CO2_PPM = Gauge('co2_ppm', 
                'CO2 Level, PPM')


# Decorate function with metric to measure duration of request
@MONITOR_REQUEST_DURATION_SECONDS.time()
def get_data(monitor):
    try:
        return(monitor.read_data())
    except Exception as error:
        stdout.write(str(error))
        stdout.flush()
        sleep(5)


if __name__ == '__main__':

    # Start up the server to expose the metrics
    start_http_server(EXPORTER_PORT)

    # Init the monitor
    try:
        mon = CO2monitor(bypass_decrypt=True)
    except Exception as error:
        stdout.write(str(error))
        stdout.flush()
        sleep(5)
        exit(1)

    while True:
        # Request data from monitor
        data = get_data(mon)
        
        # Set metrics
        CO2_PPM.set(data[1])
        TEMPERATURE_C.set(data[2])
        
        # Calculate next delay
        last_request_duration = round(MONITOR_REQUEST_DURATION_SECONDS._value.get(), 2)
        delay = REQUEST_DELAY - last_request_duration

        # Write to systemd unit log
        stdout.write(f'{data[1]}; {data[2]}; {last_request_duration}\n')

        sleep(delay)