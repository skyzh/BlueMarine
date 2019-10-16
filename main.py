#!/usr/bin/env python3
import serial
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from time import sleep
from struct import unpack
registry = CollectorRegistry()
gateway = "localhost:9092"
job = "air_quality_production"
g = Gauge('job_last_success_unixtime', 'Last time a batch job successfully finished', registry=registry)
p25 = Gauge('pm25', 'pm2.5 data ug/m^3', registry=registry)
p10 = Gauge('pm10', 'pm10 data ug/m^3', registry=registry)
points = Gauge('collected_points', 'Collected data points', registry=registry)
serial = serial.Serial('/dev/ttyUSB0', 9600)

def do_checksum(checksum, buffer):
    s = 0
    for i in buffer:
        s += i
    return checksum == s

while True:
    buffer = serial.read(32)
    if buffer[0] == 0x42 and buffer[1] == 0x4d:
        header,length,_,_p25,_p10,_,_,_,_,_,_,_,_,_,_,checksum = unpack(">HHHHHHHHHHHHHHHH", buffer)
        do_checksum(checksum, buffer[:-2])
        g.set_to_current_time()
        p25.set(_p25)
        p10.set(_p10)
        points.inc()
        push_to_gateway(gateway, job=job, registry=registry)
        print("PM2.5 %d, PM10 %d" % (_p25, _p10))
        