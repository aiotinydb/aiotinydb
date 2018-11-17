# aiotinydb
[![PyPI](https://img.shields.io/pypi/v/aiotinydb.svg)](https://pypi.python.org/pypi/aiotinydb) [![PyPI](https://img.shields.io/pypi/pyversions/aiotinydb.svg)](https://pypi.python.org/pypi/aiotinydb) [![PyPI](https://img.shields.io/pypi/l/aiotinydb.svg)](https://pypi.python.org/pypi/aiotinydb) [![Build Status](https://travis-ci.org/ASMfreaK/aiotinydb.svg?branch=master)](https://travis-ci.org/ASMfreaK/aiotinydb) [![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ASMfreaK)

asyncio compatibility shim for [`TinyDB`](https://github.com/msiemens/tinydb)

Enables usage of TinyDB in asyncio-aware contexts without slow syncronous IO.


See documentation on compatible version of [`TinyDB`](https://tinydb.readthedocs.io/en/v3.12.1/).

Basically all API calls from `TinyDB` are supported in `AIOTinyDB`. With the following exceptions: you **should not** use basic `with` syntax and `close` functions. Instead, you **should** use `async with`.  

```python
import asyncio
from aiotinydb import AIOTinyDB

async def test():
    async with AIOTinyDB('test.json') as db:
        db.insert(dict(counter=1))

loop = asyncio.new_event_loop()
loop.run_until_complete(test())
loop.close()
```

## Middleware
Any middlewares you use **should be** async-aware. See example:

```python
from tinydb.middlewares import CachingMiddleware as VanillaCachingMiddleware
from aiotinydb.middleware import AIOMiddleware

class CachingMiddleware(VanillaCachingMiddleware, AIOMiddlewareMixin):
    """
        Async-aware CachingMiddleware. For more info read
        docstring for `tinydb.middlewares.CachingMiddleware`
    """
    pass
```

If middleware requires some special handling on entry and exit, override `__aenter__` and `__aexit__`.

## Installation

```
pip install aiotinydb
```
