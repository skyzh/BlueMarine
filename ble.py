#!/usr/bin/env python3
import logging
import asyncio
import platform
from loguru import logger
from bleak import BleakClient
from config import BLE_CHARACTERISTIC_UUID, BLE_ADDR


async def ble_service(loop: asyncio.AbstractEventLoop,
                      tx: asyncio.Queue,
                      disconnected_event: asyncio.Event):

    async def put_to_queue(data):
        await tx.put(data)

    def notification_handler(sender, data):
        loop.create_task(put_to_queue(data))

    logger.info("scanning client...")

    client = BleakClient(BLE_ADDR, loop=loop)
    logger.info("connecting to device {0} ...".format(BLE_ADDR))
    await client.connect()
    x = await client.is_connected()
    logger.info("connected: {0}".format(x))

    await client.start_notify(BLE_CHARACTERISTIC_UUID, notification_handler)

    logger.info("notification registered")

    def disconnect_callback(client):
        loop.call_soon_threadsafe(disconnected_event.set)

    client.set_disconnected_callback(disconnect_callback)

    try:
        await disconnected_event.wait()
    except:
        await client.stop_notify(BLE_CHARACTERISTIC_UUID, notification_handler)

    logger.info("disconnected from device")

    await tx.put(None)

    await asyncio.sleep(0.5)
