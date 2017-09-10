import os
import unittest
import asyncio
import tempfile

class BaseCase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        self.loop.close()
        os.remove(self.file.name)
