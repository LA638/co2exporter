#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Prometheus http:8057 exporter for CO2|temperature monitoring with USB CO2 monitor
from co2meter import CO2monitor
from prometheus_client import Gauge, start_http_server
from sys import stdout
from time import sleep

exporter_port = 8057
request_delay = 10
avg_count = 4

# Creating metrics
MONITOR_REQUEST_DURATION_SECONDS = Gauge(
    'monitor_request_duration_seconds', 'USB CO2 Monitor Request Duration')
TEMPERATURE_C = Gauge('temperature_c', 'Current Temperature, C')
CO2_PPM = Gauge('co2_ppm', 'CO2 Level, PPM')

# Decorate function with metric to measure duration of request
@MONITOR_REQUEST_DURATION_SECONDS.time()
def get_data(monitor):
    try:
        return(monitor.read_data())
    except Exception as error:
        return(error)


if __name__ == '__main__':

    # Start up the server to expose the metrics
    start_http_server(exporter_port)
    # Init the monitor
    try:
        mon = CO2monitor(bypass_decrypt=True)
    except Exception as error:
        stdout.write(str(error))
        stdout.flush()
        sleep(5)
        exit(1)

    data = get_data(mon)
    CO2_PPM.set(data[1])
    old_temp = int(round(data[2]*10, 0))
    TEMPERATURE_C.set(old_temp/10)

    temp_count = 0

    # Request data
    while True:
        data = get_data(mon)
        CO2_PPM.set(data[1])
        curr_temp = int(round(data[2]*10, 0))/10
        TEMPERATURE_C.set(curr_temp)

        # Temperature averaging
        # if curr_temp == old_temp:
        #     temp_count = 0
        #     stdout.write(f'{temp_count} {old_temp} {curr_temp} No changes\n')
        #     stdout.flush()
        # else:
        #     temp_count += 1
        #     if temp_count == avg_count:
        #         TEMPERATURE_C.set(curr_temp/10)
        #         stdout.write(f'{temp_count} {old_temp} {curr_temp} Update\n')
        #         stdout.flush()
        #         old_temp = curr_temp
        #         temp_count = 0
        #     else:
        #         stdout.write(f'{temp_count} {old_temp} {curr_temp} Changed\n')
        #         stdout.flush()

        last_request_duration = MONITOR_REQUEST_DURATION_SECONDS._value.get()
        
        stdout.write(f'{data[1]}; {curr_temp}; {round(last_request_duration, 2)}\n')

        delay = request_delay - last_request_duration
        sleep(delay)
