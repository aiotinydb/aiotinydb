# Copyright 2022 d-k-bo <dkbo@mail.de>

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

"""
This module provides an AsyncIO wrapper around `fctnl.flock` to support
concurrent access from several processes on unix systems.
"""

import asyncio
from fcntl import flock, LOCK_EX, LOCK_NB, LOCK_UN
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Union, Type


if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 8):
        from typing import Literal, Protocol
    else:
        from typing_extensions import Literal, Protocol

    class HasFileno(Protocol):  # pylint: disable=missing-class-docstring, too-few-public-methods
        def fileno(self) -> int:  # pylint: disable=missing-function-docstring
            ...

    FileDescriptorLike = Union[int, HasFileno]


class AIOFileLock:
    """AsyncIO wrapper around `fctnl.flock` with an interface similar to asyncio.Lock.

    Usage:

        lock = AsyncFileLock()
        ...
        await lock.acquire()
        try:
            ...
        finally:
            lock.release()

    Context manager usage:

        lock = AsyncFileLock()
        ...
        async with lock:
             ...

    AsyncFileLock objects can be tested for locking state:

        if not lock.locked():
           await lock.acquire()
        else:
           # lock is acquired
           ...
    """
    def __init__(
        self,
        file_descriptor: 'FileDescriptorLike',
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self.file_descriptor = file_descriptor
        self.loop = loop
        self._locked: bool = False

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        self.release()

    def locked(self) -> bool:
        """Return True if lock is acquired."""
        return self._locked

    async def acquire(self) -> 'Literal[True]':
        """Acquire a lock.

        This method blocks until the lock is unlocked, then sets it to
        locked and returns True.
        """
        try:
            # avoid performance overhead of ThreadExecutor if lock is unlocked
            flock(self.file_descriptor, LOCK_EX | LOCK_NB)
        except BlockingIOError:
            # use ThreadExecutor to wait until lock is unlocked
            loop = self.loop or asyncio.get_event_loop()
            await loop.run_in_executor(None, flock, self.file_descriptor, LOCK_EX)
        self._locked = True
        return True

    def release(self) -> None:
        """Release a lock.

        When the lock is locked, reset it to unlocked, and return.

        When invoked on an unlocked lock, a RuntimeError is raised.

        There is no return value.
        """
        if self._locked:
            flock(self.file_descriptor, LOCK_UN)
            self._locked = False
        else:
            raise RuntimeError('Lock is not acquired.')
