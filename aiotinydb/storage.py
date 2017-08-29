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
from abc import abstractmethod
from tinydb.storages import Storage, JSONStorage
from aiofilelock import AIOMutableFileLock, AIOImmutableFileLock

from .exceptions import *


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

    async def __aenter__(self):
        if self._handle is None:
            try:
                self._handle = open(self._filename, 'r+')
            except FileNotFoundError:
                dirname = os.path.dirname(self._filename)
                if dirname:
                    os.makedirs(dirname, exist_ok=True)
                self._handle = open(self._filename, 'w+')
            self._lock = AIOMutableFileLock(self._handle)
            await self._lock.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        if self._handle is not None:
            await self._lock.__aexit__(exc_type, exc, traceback)
            self._lock = None
            self._handle.close()


class AIOImmutableJSONStorage(AIOJSONStorage):
    """
    Asyncronous readonly JSON Storage for AIOTinyDB
    """
    async def __aenter__(self):
        if self._handle is None:
            self._handle = open(self._filename, 'r')
            self._lock = AIOImmutableFileLock(self._handle)
            await self._lock.__aenter__()
        return self

    def write(self, data):
        raise ReadonlyStorageError('AIOImmutableJSONStorage cannot be written to')
