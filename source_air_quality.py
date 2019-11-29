import asyncio
from loguru import logger
from time import sleep
from struct import unpack
from collections import deque
from buffer_protocol import BufferProtocol
from push import p10, p25, update_data, channel_serial_error_event, channel_serial_packet_event

CHUNK_SIZE = 32


def do_checksum(checksum, buffer):
    s = 0
    for i in buffer:
        s += i
    return checksum == s


def peek_chunk(buffer: deque, length: int, clear: bool = False) -> bytes:
    x = bytearray()
    for i in range(length):
        x.append(buffer[i])
    if clear:
        for _ in range(length):
            buffer.popleft()
    return bytes(x)


def unpack_chunk(chunk: bytes):
    return unpack(">HHHHHHHHHHHHHHHH", chunk)


async def source_air_quality(loop: asyncio.AbstractEventLoop,
                             msg_queue: asyncio.Queue):
    buffer = deque()

    while True:
        data = await msg_queue.get()

        if data is None:
            break

        buffer.extend(iter(data))
        channel_serial_packet_event.inc(len(data))

        while len(buffer) >= CHUNK_SIZE:
            chunk = peek_chunk(buffer, CHUNK_SIZE)
            if chunk[0] == 0x42 and chunk[1] == 0x4d:
                _, _, _, _p25, _p10, _, _, _, _, _, _, _, _, _, _, checksum = unpack_chunk(
                    chunk)
                if do_checksum(checksum, chunk[:-2]):
                    p25.set(_p25)
                    p10.set(_p10)
                    update_data()
                    peek_chunk(buffer, CHUNK_SIZE, True)
                else:
                    buffer.clear()
                    logger.info("checksum fail, clear buffer")
                    channel_serial_error_event.inc()
            else:
                buffer.popleft()
                logger.info(
                    "wrong header, try next byte (%d remaining))" % len(buffer))
                channel_serial_error_event.inc()

        msg_queue.task_done()
