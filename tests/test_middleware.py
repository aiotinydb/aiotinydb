from . import BaseCase
from aiotinydb import AIOTinyDB
from aiotinydb.storage import AIOJSONStorage
from aiotinydb.middleware import AIOMiddleware, CachingMiddleware, AIOMiddlewareMixin
from aiotinydb.exceptions import NotOverridableError
from tinydb import TinyDB, JSONStorage
from tinydb.middlewares import Middleware

class TestMiddleware(BaseCase):
    def test_open_close(self):
        async def test():
            for middleware_cls in (AIOMiddleware, CachingMiddleware):
                async with AIOTinyDB(self.file.name, storage=middleware_cls(AIOJSONStorage)):
                    pass
        self.loop.run_until_complete(test())

    def test_not_cloaseable(self):
        with self.assertRaises(NotOverridableError):
            AIOMiddleware(JSONStorage).close()

written_to = 0
read_from = 0
closed = False
class VanillaMiddleware(Middleware):
    def __init__(self, middleware_cls):
        super(VanillaMiddleware, self).__init__(middleware_cls)
        global written_to, read_from, closed
        written_to = 0
        read_from = 0
        closed = False

    def write(self, *args):
        global written_to, read_from, closed
        written_to += 1
        return self.storage.write(*args)

    def read(self):
        global written_to, read_from, closed
        read_from += 1
        return self.storage.read()

    def close(self):
        global written_to, read_from, closed
        closed = True

class AIOVanillaMiddleware(VanillaMiddleware, AIOMiddlewareMixin):
    pass

class TestMixin(BaseCase):
    def test_mixin(self):
        global written_to, read_from, closed
        middleware = VanillaMiddleware(JSONStorage)
        with TinyDB(self.file.name, storage=middleware) as db:
            tst = 'abc'
            db.insert_multiple({'int': 1, 'char': c} for c in tst)
        self.assertGreaterEqual(read_from, 1)
        self.assertGreaterEqual(written_to, 1)
        self.assertTrue(closed)

        async def test():
            middleware = AIOVanillaMiddleware(AIOJSONStorage)
            async with AIOTinyDB(self.file.name, storage=middleware):
                tst = 'abc'
                db.insert_multiple({'int': 1, 'char': c} for c in tst)
            self.assertGreaterEqual(read_from, 1)
            self.assertGreaterEqual(written_to, 1)
            self.assertTrue(closed)
        self.loop.run_until_complete(test())
