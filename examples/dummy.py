"""This examples shows the basic usage of aioinydb."""

import asyncio

from aiotinydb import AIOTinyDB

async def do_something():
    print("Starting slow IO bound operation...")
    await asyncio.sleep(1)
    print("Completed IO bound operation.")

    return {"key": "value"}

async def main():
    print("Using 'db.json' as database.")
    async with AIOTinyDB("db.json") as db:
        document = await do_something()
        db.insert(document)
    print("Wrote database as 'db.json' to disk.")


if __name__ == "__main__":
    asyncio.run(main())
