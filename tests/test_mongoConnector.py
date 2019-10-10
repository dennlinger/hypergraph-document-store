from unittest import TestCase

import unittest, os, sys


class TestMongoParser(TestCase):
    # simply check whether the init function runs smoothly (not necessarily successfully, but gracefully)
    def test___init__(self):
        from MongoConnector import MongoConnector
        mc = MongoConnector(log_file="test.log")
        os.remove("test.log")

    def test___enter__(self):
        from MongoConnector import MongoConnector
        with MongoConnector(log_file="test.log") as mc:
            pass
        os.remove("test.log")

    def test_connection(self):
        from MongoConnector import MongoConnector
        with MongoConnector(log_file="test.log") as mc:
            articles = mc.client[mc.secrets['MONGODB_NEWS_DB']].articles
            print(articles.find_one({"title": "Rags-to-riches story of Nathan's Famous Hot Dogs"}))
        os.remove("test.log")

