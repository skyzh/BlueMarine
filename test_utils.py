import pytest
import asyncio
from utils import byte_transform, gather_packet, write_to_bp, channel_splitter
from serial_protocol import SerialProtocol
from buffer_protocol import BufferProtocol


async def read_from_queue(q: asyncio.Queue) -> list:
    x = []
    while not q.empty():
        x.append(await q.get())
    return x


async def write_to_queue(q: asyncio.Queue, b: list):
    for ch in b:
        await q.put(ch)


@pytest.mark.asyncio
async def test_should_byte_transform():
    loop = asyncio.get_event_loop()
    rx = asyncio.Queue(loop=loop)
    tx = asyncio.Queue(loop=loop)
    await write_to_queue(rx, [b"2333", b"test", None])
    await byte_transform(loop, rx, tx)
    d = await read_from_queue(tx)
    assert d == [ord('2'), ord('3'), ord('3'), ord('3'),
                 ord('t'), ord('e'), ord('s'), ord('t'),
                 None]


class SerialIOProtocol:
    def __init__(self, rx: asyncio.Queue, tx: asyncio.Queue):
        self.rx = rx
        self.tx = tx

    async def read(self) -> int:
        buf = await self.rx.get()
        self.rx.task_done()
        return buf

    async def write(self, ch: int):
        await self.tx.put(ch)

    def available(self):
        return not self.rx.empty()


@pytest.mark.asyncio
async def test_should_gather_packet():
    loop = asyncio.get_event_loop()
    rx = asyncio.Queue(loop=loop)
    tx = asyncio.Queue(loop=loop)
    sp = SerialIOProtocol(rx, tx)
    bp = BufferProtocol(sp)
    await bp.begin()
    await write_to_bp(bp, b"2333")
    await bp.end()
    await bp.begin()
    await write_to_bp(bp, b"test")
    await bp.end()
    await write_to_queue(rx, await read_from_queue(tx) + [None])
    tx = asyncio.Queue(loop=loop)
    await gather_packet(loop, bp, tx)
    data = await read_from_queue(tx)
    assert data == [b"2333", b"test", None]


@pytest.mark.asyncio
async def test_channel_splitter():
    loop = asyncio.get_event_loop()
    rx = asyncio.Queue(loop=loop)
    await write_to_queue(rx, [[0, 1, 2, 3, 4], [1, 2, 3, 3, 3], None])
    channels = [asyncio.Queue(loop=loop), asyncio.Queue(loop=loop)]
    await channel_splitter(rx, channels)
    assert (await read_from_queue(channels[0])) == [[1, 2, 3, 4], None]
    assert (await read_from_queue(channels[1])) == [[2, 3, 3, 3], None]
