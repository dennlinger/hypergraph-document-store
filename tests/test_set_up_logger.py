from unittest import TestCase

import os

class TestSet_up_logger(TestCase):

    def test_set_up_logger(self):
        from utils import set_up_logger
        from logging import Logger

        logger = set_up_logger("test", "test.log")
        self.assertIsInstance(logger, Logger)
        os.remove("test.log")
