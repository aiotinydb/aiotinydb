"""
This example demonstrates that CPU-bound operations such as `db.search()`
can be run in a process pool to prevent blocking the event loop.
"""

import asyncio
import concurrent.futures
import os
import tempfile
from typing import TypeVar

from tinydb import where
from tinydb.table import Document

from aiotinydb import AIOTinyDB

TempFileT = TypeVar("TempFileT", bound=tempfile._TemporaryFileWrapper)


async def create_db_in_process_pool(filename: str) -> None:
    global create_db  # local functions can't be pickled

    def create_db():
        async def _create_db():
            print("Creating dummy database in process pool..")
            async with AIOTinyDB(filename) as db:
                return db.insert_multiple(
                    [{hex(j): i + j for j in range(2**10)} for i in range(2**15)]
                )

        asyncio.run(_create_db())
        print("Created dummy database.")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        await asyncio.get_event_loop().run_in_executor(executor, create_db)


async def search_in_process_pool(filename: str) -> list[Document]:
    global search  # local functions can't be pickled

    def search():
        async def _search():
            print("Starting search in process pool.")
            async with AIOTinyDB(filename) as db:
                return db.search(where("0xff") == 1024)

        result = asyncio.run(_search())
        print("Completed search.")
        return result

    with concurrent.futures.ProcessPoolExecutor() as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, search)


async def still_running():
    try:
        while True:
            await asyncio.sleep(1)
            print("Event loop is still running.")
    except asyncio.CancelledError:
        pass


async def main():
    still_running_task = asyncio.create_task(still_running())

    file = tempfile.NamedTemporaryFile("r+", delete=False)
    try:
        await create_db_in_process_pool(file.name)
        await search_in_process_pool(file.name)
    finally:
        file.close()
        os.remove(file.name)

    still_running_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
