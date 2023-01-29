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

"""
Contains the base classes `AIOMiddleware` and `AIOMiddlewareMixin` for
async middlewares and implementations.
"""

# pylint: disable=too-few-public-methods
from types import TracebackType
from typing import NoReturn, Optional, Type, TypeVar
from tinydb.middlewares import Middleware
from tinydb.middlewares import CachingMiddleware as VanillaCachingMiddleware
from .exceptions import NotOverridableError
from .storage import AIOStorage

AIOMiddlewareT = TypeVar('AIOMiddlewareT', bound='AIOMiddleware')


class AIOMiddleware(Middleware):
    """
        Asyncronous middleware base class
    """
    async def __aenter__(self: AIOMiddlewareT) -> AIOMiddlewareT:
        """
            Initialize middleware here
        """
        assert isinstance(self.storage, AIOStorage)
        await self.storage.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """
            Finalize middleware here
        """
        assert isinstance(self.storage, AIOStorage)
        await self.storage.__aexit__(exc_type, exc_value, exc_tb)

    def close(self) -> NoReturn:
        """
        This is not called and should NOT be used
        """
        raise NotOverridableError('NOT to be overridden or called, use __aexit__!')


class AIOMiddlewareMixin(AIOMiddleware):
    """
        Mixin class to enable usage of non-async Middlewares
    """
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        assert isinstance(self.storage, AIOStorage)
        try:
            self.close()
        except NotOverridableError:
            pass
        await self.storage.__aexit__(exc_type, exc_value, exc_tb)


class CachingMiddleware(VanillaCachingMiddleware, AIOMiddlewareMixin):
    """
        Async-aware CachingMiddleware. For more info read
        docstring for `tinydb.middlewares.CachingMiddleware`
    """
