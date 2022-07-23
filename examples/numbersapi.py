"""
This example shows how aiotinydb can be used in the context of
asynchronous HTTP requests.
"""

__requires__ = "httpx"

import asyncio
from pprint import pp
from random import choices, randint

import httpx
from aiotinydb import AIOTinyDB
from tinydb import where

from aiotinydb.storage import AIOJSONStorage


async def main():
    numbers = {
        f"{randint(1,12)}/{randint(1,31)}"
        if tp == "date"
        else randint(1, 2000): tp
        for tp in choices(["trivia", "math", "date", "year"], k=10)
    }

    db = AIOTinyDB("numbers.json", storage=AIOJSONStorage)
    
    async with (
        httpx.AsyncClient() as http_client
    ):

        async def fetch_number(number, info_type):
            r = await http_client.get(
                f"http://numbersapi.com/{number}/{info_type}"
            )
            async with db:
                db.insert({"number": number, "type": info_type, "info": r.text})

        await asyncio.gather(
            *(
                fetch_number(number, info_type)
                for number, info_type in numbers.items()
            )
        )

    async with db:
        print("\n==== Trivia ====\n")
        pp(db.search(where("type") == "trivia"))
        print("\n==== Math ====\n")
        pp(db.search(where("type") == "math"))
        print("\n==== Dates ====\n")
        pp(db.search(where("type") == "date"))
        print("\n==== Years ====\n")
        pp(db.search(where("type") == "year"))


if __name__ == "__main__":
    asyncio.run(main())
