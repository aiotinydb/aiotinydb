import asyncio
from time import perf_counter

import aiofiles
from aiotinydb.filelock import AIOFileLock
from . import BaseCase

class TestFileLock(BaseCase):
    
    def test_filelock(self):
        async def io_operation():
            async with aiofiles.open(self.file.name) as f, AIOFileLock(f):
                await asyncio.sleep(0.5)

        async def coro():
            start_time = perf_counter()
            await asyncio.gather(io_operation(), io_operation())
            duration = perf_counter() - start_time
            assert duration > 1

        self.loop.run_until_complete(coro())

    def test_filelock_misc(self):
        async def coro():
            async with aiofiles.open(self.file.name) as f:
                lock = AIOFileLock(f)
                assert not lock.locked()
                with self.assertRaises(RuntimeError):
                    await lock.__aexit__(None, None, None)
                
        self.loop.run_until_complete(coro())
