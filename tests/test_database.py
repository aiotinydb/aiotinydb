import os
from . import BaseCase
import unittest
from aiotinydb import AIOTinyDB, DatabaseNotReady
from aiotinydb.storage import AIOImmutableJSONStorage, AIOJSONStorage
from aiotinydb.exceptions import *
from tinydb import where




class TestDBDefaults(unittest.TestCase):
    def test_default(self):
        self.assertEqual(AIOTinyDB.default_storage_class, AIOJSONStorage)

class TestDatabase(BaseCase):

    def test_uninitialized_state(self):
        db = AIOTinyDB(self.file.name)
        for meth, args in (
                ('drop_table', ('yay',)),
                ('drop_tables', tuple()),
                ('table', (db.default_table_name,)),
                ('tables', tuple())):
            with self.assertRaises(DatabaseNotReady):
                getattr(db, meth)(*args)
        for meth in ('insert', 'update', 'search'):
            with self.assertRaises(AttributeError):
                getattr(db, meth)
        with self.assertRaises(NotOverridableError):
            with db:
                pass # pragma: no cover
        with self.assertRaises(NotOverridableError):
            db.__exit__(None,None,None)
        with self.assertRaises(NotOverridableError):
            db.close()

    def test_dbops(self):
        os.unlink(self.file.name)
        async def coro():
            async with AIOTinyDB(self.file.name) as db:
                db.insert(dict(name='yay'))
                self.assertEqual(len(db), 1)
                db.truncate()
                self.assertEqual(len(db), 0)
                tst = 'abc'
                db.insert_multiple({'int': 1, 'char': c} for c in tst)
                for c, v in zip(tst, db):
                    self.assertEqual(c, v['char'])
                db.update({'int': 2}, where('int') == 1)
                self.assertEqual(len(db.search(where('int') == 2)), 3)
            async with AIOTinyDB(self.file.name, storage=AIOImmutableJSONStorage) as db:
                self.assertEqual(len(db.search(where('int') == 2)), 3)
                self.assertEqual(db.tables(), {AIOTinyDB.default_table_name})
        self.loop.run_until_complete(coro())

    def test_aiostorage_not_closeable(self):
        s = AIOImmutableJSONStorage(self.file.name)
        with self.assertRaises(NotOverridableError):
            s.close()

    def test_multiple_reopen(self):
        async def coro():
            db = AIOTinyDB(self.file.name)
            async with db:
                db.insert(dict(index='as'))
                self.assertEqual(len(db.tables()), 1)
                db.drop_table(db.default_table_name)
                self.assertEqual(len(db.tables()), 0)
            async with db:
                db.insert(dict(index='as'))
                self.assertEqual(len(db.tables()), 1)
                db.drop_tables()
                self.assertEqual(len(db.tables()), 0)
        self.loop.run_until_complete(coro())

    def test_readonly_db(self):
        async def coro():
            db = AIOTinyDB(self.file.name, storage=AIOImmutableJSONStorage)
            async with db:
                db.all()
            with self.assertRaises(ReadonlyStorageError):
                async with db:
                    db.insert({})
        self.loop.run_until_complete(coro())

    def test_alternate_tables(self):
        async def coro():
            async with AIOTinyDB(self.file.name) as db:
                db.insert(dict(index='default'))
                db.table('alt').insert(dict(index='alt'))
                self.assertEqual(len(db.tables()), 2)
                self.assertEqual(len(db), 1)
                self.assertEqual(len(db.table(db.default_table_name)), 1)
                self.assertEqual(len(db.table('alt')), 1)
        self.loop.run_until_complete(coro())
