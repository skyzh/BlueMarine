import asyncio
from loguru import logger
from buffer_protocol import BufferProtocol, BUFFER_T_END

async def byte_transform(loop: asyncio.AbstractEventLoop, rx: asyncio.Queue, tx: asyncio.Queue):
    while True:
        buffer = await rx.get()
        if buffer is None:
            await tx.put(None)
            return
        for b in buffer:
            await tx.put(b)
        rx.task_done()

async def gather_packet(loop: asyncio.AbstractEventLoop, bp: BufferProtocol, tx: asyncio.Queue):
    buffer = bytearray()
    while True:
        ch = await bp.read()
        if ch is None:
            await tx.put(None)
            return
        if ch >= 0:
            buffer.append(ch)
        if ch == BUFFER_T_END:
            await tx.put(bytes(buffer))
            buffer.clear()

async def write_to_bp(bp: BufferProtocol, buffer: bytes):
    for b in buffer:
        await bp.write(b)

async def channel_splitter(rx: asyncio.Queue, txs: [asyncio.Queue]):
    while True:
        buf = await rx.get()
        if buf is None:
            for tx in txs:
                await tx.put(None)
            return
        if len(buf) == 0:
            logger.warning("received packet of 0 length")
            continue
        if buf[0] >= len(txs):
            logger.warning(f"requested #{buf[0]} out of #{len(txs)}")
            continue
        await txs[buf[0]].put(buf[1:])
        rx.task_done()
        
async def info(rx: asyncio.Queue):
    while True:
        buf = await rx.get()
        if buf is None:
            return
        logger.warning(buf)
        rx.task_done()