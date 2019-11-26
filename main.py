#!/usr/bin/env python3
import asyncio
from loguru import logger
from ble import ble_service
from serial_protocol import SerialProtocol
from buffer_protocol import BufferProtocol
from utils import byte_transform, gather_packet, channel_splitter, info
from source_air_quality import source_air_quality
from source_temperature import source_temperature
from push import buffer_queue_stat, serialpb_packet_event


async def main(loop: asyncio.AbstractEventLoop,
               end_event: asyncio.Event):
    rx_tx_1 = asyncio.Queue(loop=loop)
    ble = ble_service(loop, rx_tx_1, end_event)  # --> tx1
    rx_tx_2 = asyncio.Queue(loop=loop)
    bt = byte_transform(loop, rx_tx_1, rx_tx_2)  # <-- rx1 -> tx2
    sp = SerialProtocol(rx_tx_2)  # <- rx2
    bp = BufferProtocol(sp)
    rx_tx_3 = asyncio.Queue(loop=loop)
    gp = gather_packet(loop, bp, rx_tx_3)  # -> tx3
    rx_tx_4 = asyncio.Queue(loop=loop)
    stat = buffer_queue_stat(
        rx_tx_3, rx_tx_4, serialpb_packet_event)  # <- rx3 -> tx4
    channels = [asyncio.Queue(loop=loop),  # protobuf
                asyncio.Queue(loop=loop),  # serial
                asyncio.Queue(loop=loop)]  # logging
    cs = channel_splitter(rx_tx_4, channels)  # <- rx4 -> channels
    src_temperature = source_temperature(loop, channels[0])
    src_air_quality = source_air_quality(loop, channels[1])
    src_log = info(channels[2])
    await asyncio.gather(ble, bt, gp, cs, stat,
                         src_temperature, src_air_quality,
                         src_log)
    logger.info("cleaning up...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    try:
        loop.run_until_complete(main(loop, event))
    finally:
        logger.info("disconnecting...")
        event.set()
    loop.close()
