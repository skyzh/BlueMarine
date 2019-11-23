import asyncio

class SerialProtocol:
    def __init__(self, rx: asyncio.Queue):
        self.rx = rx

    async def read(self) -> int:
        buf = await self.rx.get()
        self.rx.task_done()
        return buf

    async def write(self, ch: int):
        raise "not implemented"

    def available(self):
        return not self.rx.empty()
