import asyncio
from loguru import logger
from time import sleep
from struct import unpack
from collections import deque
from buffer_protocol import BufferProtocol
from push import temp, hum, pa, channel_pb_packet_event, channel_pb_error_event
from sense_pb2 import SenseUpdate

TEMP = 1
HUM = 2
PA = 3

async def source_temperature(loop: asyncio.AbstractEventLoop,
                             msg_queue: asyncio.Queue):
    while True:
        data = await msg_queue.get()

        if data is None:
            return

        sense_update = SenseUpdate()
        try:
            sense_update.ParseFromString(data)
        except:
            logger.warning("error when decoding protobuf packet")
            channel_pb_error_event.inc()
            msg_queue.task_done()
            continue

        field = sense_update.field

        target = None
        if field == TEMP:
            target = temp
        if field == HUM:
            target = hum
        if field == PA:
            target = pa
        
        if target is None:
            logger.warning("target %s not found" % field)
            channel_pb_error_event.inc()
        else:
            target.set(sense_update.data)
        
        channel_pb_packet_event.inc()
        msg_queue.task_done()
