# aiotinydb - asyncio compatibility shim for tinydb

# Copyright 2017 Pavel Pletenev <cpp.create@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=super-init-not-called
import os
import io
import json
from abc import abstractmethod
from types import TracebackType
from typing import Any, Dict, Optional, NoReturn, Type, TypeVar, Union
import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper
from tinydb.storages import Storage, JSONStorage
from .exceptions import NotOverridableError, ReadonlyStorageError

try:
    # `fcntl.flock()` is only available on unix
    from .filelock import AIOFileLock
    FILELOCK_SUPPORTED = True
except ImportError:  # pragma: no cover
    FILELOCK_SUPPORTED = False  # pragma: no cover

AIOStorageT = TypeVar('AIOStorageT', bound='AIOStorage')
AIOJSONStorageT = TypeVar('AIOJSONStorageT', bound='AIOJSONStorage')
StrOrBytesPath = Union[str,  bytes, 'os.PathLike[str]', 'os.PathLike[bytes]']


class AIOStorage(Storage):
    """
    Abstract asyncio Storage class
    """
    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    async def __aenter__(self: AIOStorageT) -> AIOStorageT:
        """
        Initialize storage in async manner (open files, connections, etc...)
        """
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Finalize storage in async manner (close files, connections, etc...)
        """
        raise NotImplementedError('To be overridden!')

    def close(self) -> NoReturn:
        """
        This is not called and should NOT be used
        """
        raise NotOverridableError('NOT to be overridden or called, use __aexit__!')


class AIOJSONStorage(AIOStorage, JSONStorage):
    """
    Asyncronous JSON Storage for AIOTinyDB
    """
    def __init__(self, filename: StrOrBytesPath, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self._filename = filename
        self._file: Optional[AsyncTextIOWrapper] = None
        self._lock: Optional['AIOFileLock'] = None
        self._handle: Optional[io.StringIO] = None

    async def __aenter__(self: AIOJSONStorageT) -> AIOJSONStorageT:
        if self._handle is None:
            try:
                self._file = await aiofiles.open(self._filename, 'r+')
            except FileNotFoundError:
                dirname = os.path.dirname(self._filename)
                if dirname:
                    os.makedirs(dirname, exist_ok=True)

                self._file = await aiofiles.open(self._filename, 'w+')

            if FILELOCK_SUPPORTED:
                self._lock = AIOFileLock(self._file)
                await self._lock.acquire()
            self._handle = io.StringIO(await self._file.read())
        return self

    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        assert isinstance(self._handle, io.StringIO)
        self._handle.seek(0)
        serialized = json.dumps(data, **self.kwargs)
        self._handle.write(serialized)
        self._handle.flush()
        self._handle.truncate()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        if self._handle is not None:
            assert self._file is not None

            await self._file.seek(0)
            await self._file.write(self._handle.getvalue())
            await self._file.flush()
            await self._file.truncate()
            if FILELOCK_SUPPORTED:
                assert self._lock is not None
                self._lock.release()
                self._lock = None
            await self._file.close()
            self._handle.close()
            self._file = None
            self._handle = None


class AIOImmutableJSONStorage(AIOJSONStorage):
    """
    Asyncronous readonly JSON Storage for AIOTinyDB
    """
    async def __aenter__(self: AIOJSONStorageT) -> AIOJSONStorageT:
        if self._handle is None:
            self._file = await aiofiles.open(self._filename, 'r')
            if FILELOCK_SUPPORTED:
                self._lock = AIOFileLock(self._file)
                await self._lock.acquire()
            self._handle = io.StringIO(await self._file.read())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        if self._handle is not None:
            assert self._file is not None

            if FILELOCK_SUPPORTED:
                assert self._lock is not None
                self._lock.release()
                self._lock = None
            await self._file.close()
            self._handle.close()
            self._file = None
            self._handle = None

    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        raise ReadonlyStorageError('AIOImmutableJSONStorage cannot be written to')
