#!/usr/bin/env python3
import asyncio
from loguru import logger
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from time import sleep
from struct import unpack
from collections import deque

registry = CollectorRegistry()
gateway = "localhost:9092"
job = "air_quality_production"
g = Gauge('job_last_success_unixtime', 'Last time a batch job successfully finished', registry=registry)
p25 = Gauge('pm25', 'pm2.5 data ug/m^3', registry=registry)
p10 = Gauge('pm10', 'pm10 data ug/m^3', registry=registry)
points = Gauge('collected_points', 'Collected data points', registry=registry)

CHUNK_SIZE = 32

def do_checksum(checksum, buffer):
    s = 0
    for i in buffer:
        s += i
    return checksum == s

def get_chunk(buffer: deque, length: int) -> bytes:
    x = bytearray()
    for _ in range(length):
        x.append(buffer.popleft())
    return bytes(x)

def unpack_chunk(chunk: bytes):
    return unpack(">HHHHHHHHHHHHHHHH", chunk)

async def push_service(loop: asyncio.AbstractEventLoop, 
                       msg_queue: asyncio.Queue):
    logger.info("loop start")

    buffer = deque()

    while True:
        data = await msg_queue.get()
        
        if data is None:
            logger.info("loop exit")
            break

        buffer.extend(iter(data))
        
        while len(buffer) >= CHUNK_SIZE:
            chunk = get_chunk(buffer, CHUNK_SIZE)
            if chunk[0] == 0x42 and chunk[1] == 0x4d:
                _,_,_,_p25,_p10,_,_,_,_,_,_,_,_,_,_,checksum = unpack_chunk(chunk)
                if do_checksum(checksum, chunk[:-2]):
                    g.set_to_current_time()
                    p25.set(_p25)
                    p10.set(_p10)
                    points.inc()
                    push_to_gateway(gateway, job=job, registry=registry)
                    logger.info(f"PM2.5 {_p25}, PM10 {_p10}")
                else:
                    buffer.clear()
                    logger.info("checksum fail, clear buffer")
            else:
                buffer.popleft()
                logger.info(f"wrong header, try next byte ({len(buffer)} remaining)")

        msg_queue.task_done()
