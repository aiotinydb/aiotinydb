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
Contains the error types for aiotinydb.
"""


class AIOTinyDBError(Exception):
    """Base class for AIOTinyDB exceptions"""


class DatabaseNotReady(AIOTinyDBError):
    """Indicates wrong usage of AIOTinyDB"""


class ReadonlyStorageError(AIOTinyDBError):
    """Raised when a readonly storage is attempted to be written to"""


class NotOverridableError(AIOTinyDBError):
    """Indicates a non-overridable method"""
