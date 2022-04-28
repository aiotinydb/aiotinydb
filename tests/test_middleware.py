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


class VanillaMiddleware(Middleware):
    def __init__(self, middleware_cls):
        super().__init__(middleware_cls)
        self.written_to = 0
        self.read_from = 0
        self.closed = False

    def write(self, *args):
        self.written_to += 1
        return self.storage.write(*args)

    def read(self):
        self.read_from += 1
        return self.storage.read()

    def close(self):
        self.closed = True
        self.storage.close()

class AIOVanillaMiddleware(VanillaMiddleware, AIOMiddlewareMixin):
    pass

class TestMixin(BaseCase):
    def test_mixin(self):
        sync_middleware = VanillaMiddleware(JSONStorage)
        with TinyDB(self.file.name, storage=sync_middleware) as sync_db:
            tst = 'abc'
            sync_db.insert_multiple({'int': 1, 'char': c} for c in tst)
        assert sync_middleware.read_from
        assert sync_middleware.written_to
        assert sync_middleware.closed

        async def test():
            async_middleware = AIOVanillaMiddleware(AIOJSONStorage)
            async with AIOTinyDB(self.file.name, storage=async_middleware) as async_db:
                tst = 'abc'
                async_db.insert_multiple({'int': 1, 'char': c} for c in tst)
            assert async_middleware.read_from
            assert async_middleware.written_to
            assert async_middleware.closed
        self.loop.run_until_complete(test())
