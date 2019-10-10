"""
This file reads the documents with specified values from the MongoDB, and readies them for insertion into the
Postgres schema. This is a separate class, since we want to avoid running it with every try/experimentation over
the 'regular' schema, which could potentially have several reworks. The stored documents, on the other hand,
should be relatively fixed, and not require constant reworks.
Some words on the naming convention: The name from the 'articles' table in MongoDB was renamed to 'documents', since
this is the common phrase used in the paper, as well as the context of 'document collections'.
"""

from MongoConnector import MongoConnector
from PostgresConnector import PostgresConnector

from utils import set_up_logger, check_table_existence
from psycopg2 import ProgrammingError, IntegrityError
from psycopg2.extras import execute_values

import os
import time
import logging
from collections import OrderedDict


class DocumentGenerator:
    def __init__(self,
                 fields=OrderedDict({"_id":"document_id",
                                     "title":"title",
                                     "feedName":"feedName",
                                     "category":"category",
                                     "feedURL":"feedURL",
                                     "published":"published"
                                     }),
                 num_distinct_documents=0,
                 document_table_name="documents",
                 database="postgres",
                 user="postgres",
                 password="postgres",
                 host="127.0.0.1",
                 port=5435,
                 log_file=os.path.join(os.path.dirname(__file__), "logs/DocumentGenerator.log"),
                 log_level=logging.INFO,
                 log_verbose=True
                 ):
        """
        Initializes context, and sets up documents that will be parsed.
        Also establishes the PostgresConnector that will later be used to push the retrieved documents.
        :param fields: (OrderedDict) Key-value pairs that indicate a mapping of fields that should be retrieved (key),
               and the respective field it should be called in the SQL table. Ordered because SQL tables are.
        :param num_distinct_documents: (int) As the name indicates, the number of distinct articles that should be used.
               Mainly for debugging purposes. 0 means all documents will be used, in accordance with MongoDB standards.
        :param document_table_name: (str) Name of the Postgres table that should contain the documents
        :param database: (str) database name.
        :param user: (str) User name to get access to the Postgres database.
        :param password: (str) Corresponding user password.
        :param host: (IP) IP address (in string format) for the host of the postgres database.
        :param port: (integer) Port at which to access the database.
        :param log_file: (os.path) Path to the file containing the logs.
        :param log_level: (logging.LEVEL) Specifies the level to be logged.
        :param log_verbose: (boolean) Specifies whether or not to look to stdout as well.
        """

        # set up logger
        self.logger = set_up_logger(__name__, log_file, log_level, log_verbose)
        self.logger.info("Successfully registered logger to DocumentGenerator.")

        # register a MongoConnector
        self.mc = MongoConnector()
        self.logger.info("Successfully registered MongoConnector to DocumentGenerator.")

        self.num_distinct_documents = num_distinct_documents
        # get the distinct IDs for the documents so we can match against them later
        if self.num_distinct_documents != 0:
            self.logger.info("Non-zero limit detected. Fetching first N distinct document IDs now...")
            with self.mc as open_mc:
                documents = open_mc.client[open_mc.news].articles
                self.first_documents = list(documents.find().limit(self.num_distinct_documents))
                # for small enough number, and large enough document collection, this is more efficient:
                self.first_documents = [el["_id"] for el in self.first_documents]
                self.logger.info("Successfully registered relevant document IDs.")
        else:
            # needed to avoid later conflicts
            self.first_documents = []
        # set up PostgresConnector. Since we only use these once, I don't see any reason to store the connection
        # details locally again.
        self.pc = PostgresConnector(database, user, password, host, port)
        self.logger.info("Successfully registered PostgresConnector to DocumentGenerator.")

        # format them into a reasonable format
        self.fields = fields
        if not self.fields:
            self.logger.error("No fields for MongoDB table specified!")
        self.values_to_retrieve = {key: 1 for key in self.fields.keys()}
        # suppress _id if not wanted, as it is returned by default.
        if "_id" not in self.values_to_retrieve.keys():
            self.values_to_retrieve["_id"] = 0
        # TODO
        self.sql_format = ", ".join([value for value in self.fields.values()])
        self.document_table_name = document_table_name

        # preparation for later. According to PEP8
        self.data = []
        self.logger.info("Successfully set up DocumentGenerator.")

    def retrieve(self):
        """
        Get values from MongoDB ready for offline processing, and later insertion. So far the software pattern for
        the insertion into Postgres is unclear, but will likely also be done in that class. Hopefully the design of the
        PostgresConnector holds up so that we do not have to duplicate several elements.
        :return: (None) Internally generates the value tuples required for insertion into Postgres.
        """

        self.logger.info("Starting to retrieve documents from MongoDB...")
        start_time = time.time()

        with self.mc as open_mc:
            documents = open_mc.client[open_mc.news].articles
            if self.first_documents:
                self.data = list(documents.find({"_id": {"$in": self.first_documents}}, self.values_to_retrieve))
            else:
                # self.first_documents will be empty if no limit is specified!
                self.data = list(documents.find({}, self.values_to_retrieve))
            # get out of dictionary key structure:
            self.data = [list(el.values()) for el in self.data]

        end_time = time.time()
        self.logger.info("Successfully retrieved relevant documents in {:.4f} s.".format(end_time - start_time))

    def push(self):
        """
        Pushes a previously collected series of documents from the local store to a Postgres table, as per the defined
        schema. This should also check that the documents have been actually retrieved before.
        :return: (None) Fills up the (remote) postgres table.
        """
        self.logger.info("Starting to push values into the Postgres table...")

        if not self.data:
            self.logger.error("No data found to be pushed! Please call .retrieve() first!")
            return 0

        with self.pc as open_pc:
            if not check_table_existence(self.logger, open_pc, self.document_table_name):
                return 0
            self.logger.info("Found document table.")

            self.logger.info("Inserting values.")

            # build query
            start_time = time.time()
            try:
                execute_values(open_pc.cursor,
                               "INSERT INTO {} ({}) VALUES %s".format(self.document_table_name, self.sql_format),
                               self.data)

                end_time = time.time()
                self.logger.info("Successfully inserted values in {:.4f} s".format(end_time - start_time))
            except IntegrityError as err:
                self.logger.error("Values with previously inserted primary key detected!\n {}".format(err))
                return 0

    def clear(self):
        """
        Deletes previously inserted documents from the table.
        :return: (None). Calls Postgres table with prepared DELETE-statement.
        """
        with self.pc as open_pc:
            if not check_table_existence(self.logger, open_pc, self.document_table_name):
                return 0
            self.logger.info("Found document table.")

            self.logger.info("Deleting all previously inserted documents...")
            open_pc.cursor.execute("DELETE FROM {}".format(self.document_table_name))
            # TODO: Check whether document count is actually 0!
            self.logger.info("Successfully deleted all previously inserted documents.")

    def remove_spike(self):
        """
        Manual deletion of the exceptionally high volume on the two dates of 18th and 28th of August 2016.
        :return: (None)
        """
        with self.pc as open_pc:
            if not check_table_existence(self.logger, open_pc, self.document_table_name):
                return 0
            self.logger.info("Found document table.")
            start = time.time()
            self.logger.info("Deleting all previously inserted documents...")
            open_pc.cursor.execute("DELETE FROM {} " \
                                   "WHERE ((published >= '2016-08-18 10:00:00' AND published < '2016-08-18 12:00:00') "
                                   "OR (published >= '2016-08-28 10:00:00' AND published < '2016-08-28 12:00:00') " 
                                   "OR (published >= '2016-08-18 14:00:00' AND published < '2016-08-18 17:00:00') "
                                   "OR (published >= '2016-08-28 14:00:00' AND published < '2016-08-28 17:00:00')) "
                                   "AND feedName = 'WP'".format(self.document_table_name))
            end = time.time()
            self.logger.info("Successfully deleted all documents during the peak time in {:.4f} s.".format(end-start))


if __name__ == "__main__":
    dg = DocumentGenerator()
    dg.retrieve()
    # print(dg.data)
    print(dg.data[0])
    dg.clear()
    dg.push()
