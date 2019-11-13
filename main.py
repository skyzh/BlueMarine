from loguru import logger
import asyncio

from ble import ble_service
from push import push_service

async def main(loop: asyncio.AbstractEventLoop, q: asyncio.Queue):
    await asyncio.gather(
        ble_service(loop, q),
        push_service(loop, q))
    logger.info("cleaning up...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(loop=loop)
    loop.run_until_complete(main(loop, q))
    loop.close()
    