# aiotinydb
[![PyPI](https://img.shields.io/pypi/v/aiotinydb.svg)](https://pypi.python.org/pypi/aiotinydb) [![PyPI](https://img.shields.io/pypi/pyversions/aiotinydb.svg)](https://pypi.python.org/pypi/aiotinydb) [![PyPI](https://img.shields.io/pypi/l/aiotinydb.svg)](https://pypi.python.org/pypi/aiotinydb) [![Build Status](https://travis-ci.org/ASMfreaK/aiotinydb.svg?branch=master)](https://travis-ci.org/ASMfreaK/aiotinydb) [![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ASMfreaK)
asyncio compatibility shim for tinydb

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
