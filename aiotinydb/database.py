"""
    aiotinydb - asyncio compatibility shim for tinydb

    Copyright 2017 Pavel Pletenev <cpp.create@gmail.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# pylint: disable=super-init-not-called,arguments-differ
# pylint: disable=too-many-instance-attributes
from asyncio import Lock
from typing import Optional, Union
from tinydb import TinyDB
from tinydb.table import Table
from .exceptions import NotOverridableError, DatabaseNotReady
from .middleware import AIOMiddleware
from .storage import AIOJSONStorage, AIOStorage


class AIOTinyDB(TinyDB):
    """
    TinyDB for asyncio

    # Example
    ```
    import asyncio
    from aiotinydb import AIOTinyDB

    async def test():
        async with AIOTinyDB('test.json') as db:
            db.insert(dict(counter=1))

    loop = asyncio.new_event_loop()
    loop.run_until_complete(test())
    loop.close()
    ```
    """
    # The class that will be used to create table instances
    table_class = Table
    # The class that will be used by default to create storage instances
    default_storage_class = AIOJSONStorage

    def __init__(self, *args, **kwargs):
        storage = kwargs.pop('storage', self.default_storage_class)
        self._storage: Union[AIOStorage, AIOMiddleware] = storage(*args, **kwargs)
        self._opened: bool = False
        self._tables = {}
        self._lock: Optional[Lock] = None

    def drop_table(self, name):
        if not self._opened:
            raise DatabaseNotReady('File is not opened. Use `async with AIOTinyDB(...):`')
        return super().drop_table(name)

    def drop_tables(self):
        if not self._opened:
            raise DatabaseNotReady('File is not opened. Use `async with AIOTinyDB(...):`')
        return super().drop_tables()

    def table(self, name: str, **kwargs):
        if not self._opened:
            raise DatabaseNotReady('File is not opened. Use `async with AIOTinyDB(...):`')
        return super().table(name, **kwargs)

    def tables(self):
        if not self._opened:
            raise DatabaseNotReady('File is not opened. Use `async with AIOTinyDB(...):`')
        return super().tables()

    def __getattr__(self, val):
        if not self._opened:
            raise AttributeError('File is not opened. Use `async with AIOTinyDB(...):`')
        return super().__getattr__(val)

    async def __aenter__(self):
        if self._lock is None:
            self._lock = Lock()
        await self._lock.acquire()
        if not self._opened:
            await self._storage.__aenter__()
            self._opened = True
            self._tables[self.default_table_name] = self.table(self.default_table_name)
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        if self._opened:
            self._opened = False
            await self._storage.__aexit__(exc_type, exc, traceback)
            self._tables = {}
        assert self._lock is not None
        self._lock.release()

    def close(self):
        raise NotOverridableError('Usual methods will not work on async')

    def __enter__(self):
        raise NotOverridableError('Usual methods will not work on async')

    def __exit__(self, exc_type, exc, tb):
        raise NotOverridableError('Usual methods will not work on async')
