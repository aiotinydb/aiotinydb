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
# pylint: disable=super-init-not-called
import os
import io
from abc import abstractmethod

import aiofiles
import aiofilelock
from tinydb.storages import Storage, JSONStorage

from .exceptions import NotOverridableError, ReadonlyStorageError


class AIOStorage(Storage):
    """
    Abstract asyncio Storage class
    """
    @abstractmethod
    async def __aenter__(self):
        """
        Initialize storage in async manner (open files, connections, etc...)
        """
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    async def __aexit__(self, exc_type, exc, traceback):
        """
        Finalize storage in async manner (close files, connections, etc...)
        """
        raise NotImplementedError('To be overridden!')

    def close(self):
        """
        This is not called and should NOT be used
        """
        raise NotOverridableError('NOT to be overridden or called, use __aexit__!')


class AIOJSONStorage(AIOStorage, JSONStorage):
    """
    Asyncronous JSON Storage for AIOTinyDB
    """
    def __init__(self, filename, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._filename = filename
        self._lock = None
        self._handle = None
        self._aio_handle = None
        self._enable_write = True

    async def __aenter__(self):
        if self._handle is None:
            try:
                self._aio_handle = await aiofiles.open(self._filename, 'r+')
            except FileNotFoundError:
                dirname = os.path.dirname(self._filename)
                if dirname:
                    os.makedirs(dirname, exist_ok=True)

                self._aio_handle = await aiofiles.open(self._filename, 'w+')

            self._lock = aiofilelock.AIOMutableFileLock(self._aio_handle._file)
            await self._lock.acquire()

            payload = await self._aio_handle.read()
            self._handle = io.StringIO(payload)
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        if self._handle is not None:
            if self._enable_write:
                await self._aio_handle.seek(0)
                await self._aio_handle.write(self._handle.getvalue())

            await self._lock.close()
            await self._aio_handle.close()
            self._handle.close()


class AIOImmutableJSONStorage(AIOJSONStorage):
    """
    Asyncronous readonly JSON Storage for AIOTinyDB
    """
    def __init__(self, filename, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)

        self._enable_write = False

    async def __aenter__(self):
        if self._handle is None:
            self._aio_handle = await aiofiles.open(self._filename, 'r')
            self._lock = aiofilelock.AIOMutableFileLock(self._aio_handle._file)
            await self._lock.acquire()

            payload = await self._aio_handle.read()
            self._handle = io.StringIO(payload)
        return self

    def write(self, data):
        raise ReadonlyStorageError('AIOImmutableJSONStorage cannot be written to')
