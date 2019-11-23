import asyncio

BUFFER_T_BEGIN = -1
BUFFER_T_END =  -2

class BufferProtocol(object):
    def __init__(self, sp):
        self.sp = sp
        self.recv_cnt = 0
        self.send_cnt = 0
        self.recv_ch = 0
        self.send_ch = 0
        self.transaction_begin = False

    async def read(self) -> int:
        while True:
            ch = await self.sp.read()
            if ch is None:
                return None
            if ch & 0x80:
                if ch == 0xff:
                    self.recv_cnt = 0
                    self.transaction_begin = True
                    return BUFFER_T_BEGIN
                else:
                    self.transaction_begin = False
                    return BUFFER_T_END
            else:
                if not self.transaction_begin:
                    continue
                x = self.recv_ch | (ch >> (7 - self.recv_cnt))
                self.recv_cnt += 1
                if self.recv_cnt == 8:
                    self.recv_cnt = 0
                    self.recv_ch = 0
                else:
                    self.recv_ch = (ch << self.recv_cnt) & 0xff
                if self.recv_cnt != 1:
                    return x
    
    async def write(self, ch: int):
        self.send_cnt += 1
        x = self.send_ch | ch >> self.send_cnt
        self.send_ch = (ch << (7 - self.send_cnt)) & 0xff & ~0x80
        await self.sp.write(x)
        if self.send_cnt == 7:
            await self.sp.write(ch & 0xff & ~0x80)
            self.send_cnt = 0
            self.send_ch = 0

    async def begin(self):
        await self.sp.write(0xff)
        self.send_ch = 0
        self.send_cnt = 0

    async def end(self):
        if self.send_cnt != 0:
            await self.sp.write(self.send_ch)
        await self.sp.write(0xfe)
