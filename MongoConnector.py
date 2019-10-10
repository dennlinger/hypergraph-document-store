"""
Defines the basic MongoDB connector class.
Supposed goals:
- Establish connection to MongoDB (through SSH Tunnel, else this whole class is kind of pointless, since PyMongo already supports
  most of that functionality per default.)
- Retrieve results from a given connection
- Specify more precise results (date range, fields, etc.) (maybe)


"""

import pymongo
import json
import os
import logging

from sshtunnel import SSHTunnelForwarder
from pymongo.errors import OperationFailure
from bson import ObjectId

from utils import set_up_logger


class MongoConnector:
    def __init__(self,
                 secrets=os.path.join(os.path.dirname(__file__), "secrets.json"),
                 log_file=os.path.join(os.path.dirname(__file__), "logs/MongoConnector.log"),
                 log_level=logging.INFO,
                 log_verbose=True):
        """
        :param secrets: (os.path) Path to the file containing the relevant parameters for the login via a SSHTunnel
                into the MongoDB. Will be treated as a JSON object (i.e. dictionary in Python), and must contain
                the following parameters:
                SSH_HOST, specifies the tunnel address
                LDAP_USER, user name for ssh login
                LDAP_PASSWORD, corresponding password
                MONGODB_PORT, usually 27016 (careful, this has to be an integer)
                MONGODB_HOST, host address of the mongodb, usually localhost
                MONGODB_AUTH_DB, database which is owned by user
                MONGODB_AUTH_USER, username for mongodb
                MONGODB_AUTH_PW, corresponding password
                MONGODB_NEWS_DB, database which contains the relevant news articles.
                        Default location is assumed to be in the same directory as the class definition.
        :param log_file: (os.path) Path to the file containing the logs
        :param log_level: (logging.LEVEL) Specifies the level to be logged
        :param log_verbose: (boolean) Specifies whether or not to look to stdout as well.
        """
        # read secrets
        with open(secrets, "r") as secret_file:
            self.secrets = json.load(secret_file)

        # set up log file. Specify name and level, and also print message time to it.
        self.logger = set_up_logger(__name__, log_file, log_level, log_verbose)
        self.logger.info("Successfully registered logger to MongoConnector.")
        # name abstraction, since it is frequently used
        self.news = self.secrets['MONGODB_NEWS_DB']

    def __enter__(self):
        """
        Establish connection with MongoDB.
        See https://dbsvm-hiwi.ifi.uni-heidelberg.de/wiki/index.php/Access_a_MongoDB_database_on_adrastea_with_a_SSH_tunnel_from_Python_or_Java
        We'll use the enter statement as there could be potentially multiple requests to the same database in
        one context, and it would be costly to establish the connection every time.
        __enter__ and __exit__ are the proper way in Python, as it seems.
        :return: self.
        """
        # Necessary authentication via tunnel
        self.server = SSHTunnelForwarder((self.secrets['SSH_HOST'], 22), ssh_username=self.secrets['LDAP_USER'],
                                         ssh_password=self.secrets['LDAP_PASSWORD'],
                                         remote_bind_address=('localhost', self.secrets['MONGODB_PORT']),
                                         local_bind_address=('localhost', self.secrets['MONGODB_PORT']))
        self.server.start()
        self.logger.info('Connected via SSH and established Port-Forwarding...')

        self.client = pymongo.MongoClient(self.secrets['MONGODB_HOST'],
                                          self.secrets['MONGODB_PORT'],
                                          appname="hypergraph_parser")
        try:
            self.client[self.secrets['MONGODB_AUTH_DB']].authenticate(self.secrets['MONGODB_AUTH_USER'],
                                                                      self.secrets['MONGODB_AUTH_PW'])
            self.logger.info('Successfully authenticated on MongoDB.')
            # list connections for both own user and the news dataset (assumes you have read rights there
            self.logger.info('Available Collections in AdminDB ' + self.secrets['MONGODB_AUTH_DB'] + ': ')
            self.logger.info('\t' + str(self.client[self.secrets['MONGODB_AUTH_DB']].list_collection_names()))
            self.logger.info('Available Collections in NewsDB ' + self.secrets['MONGODB_NEWS_DB'] + ': ')
            self.logger.info('\t' + str(self.client[self.news].list_collection_names()))

        except OperationFailure as err:
            self.logger.error('Authentication with MongoDB failed. See stack trace below for more information.')
            self.logger.exception(err)
            self.client.close()
            self.logger.info('Closed connection.')

        return self

    # clean up
    def __exit__(self, exception_type, exception_value, traceback):
        """
        See https://docs.quantifiedcode.com/python-anti-patterns/correctness/exit_must_accept_three_arguments.html
        Idea taken from https://stackoverflow.com/questions/865115/how-do-i-correctly-clean-up-a-python-object
        :param exception_type: Type of exception caught. Needed for errors only.
        :param exception_value: Value during exception.
        :param traceback: Traceback. Should be handled automatically.
        :return: None
        """
        self.client.close()
        self.logger.info("Connection with MongoDB successfully closed.")
        # self.server.stop() is alias
        self.server.close()
        self.logger.info("Connection with host successfully closed.")


if __name__ == "__main__":
    with MongoConnector() as mc:
        articles = mc.client[mc.news].articles

        print(articles.find_one({"title": "Rags-to-riches story of Nathan's Famous Hot Dogs"}, no_cursor_timeout=True))

        sentences = mc.client[mc.news].sentences
        print(sentences.find_one({"_id": 581}))

        pos = mc.client[mc.news].pos
        print(pos.find_one({"_id": ObjectId("58778b2952faff9ef9527743")}))
