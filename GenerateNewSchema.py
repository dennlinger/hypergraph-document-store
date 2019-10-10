"""
For different Graph models, we need additional tables potentially in the same databse.
Technically, we could also create new docker containers, but then we additionally have duplicated entries for
the whole document collection.
"""

from PostgresConnector import PostgresConnector
from HyperedgeGenerator import HyperedgeGenerator
from utils import check_table_existence, set_up_logger

import argparse
import logging
import os
import sys

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_parser():
    """
    Creates an argument parser with the relevant options.
    :return: (argparser) Argument handle.
    """
    args = argparse.ArgumentParser(description="Process all tables.")

    args.add_argument("-p", "--port", type=int, default=5436,
                      help="Port for a new docker container.")
    args.add_argument("-f", "--prefix", type=str, default="entity",
                      help="Prefix tag for the generated tables.")
    args.add_argument("-e", "--entities-only", type=str2bool, default=True,
                      help="Whether or not only entities should be processed.")
    args.add_argument("-w", "--window-size", type=int, default=2,
                      help="The window size for the processed documents.")

    parsed = args.parse_args()
    return parsed


class SchemaCreator:

    def __init__(self,
                 prefix="entity",
                 window_size=2,
                 entities_only=True,
                 port=5436,
                 log_file=os.path.join(os.path.dirname(__file__), "logs/SchemaCreator.log"),
                 log_level=logging.INFO,
                 log_verbose=True
                 ):
        """
        Set up.
        :param prefix: (str) Prefix to the table names.
        :param port: (int) Used to connect to the Postgres tables.
        :param log_file: (os.path) Path to the file containing the logs.
        :param log_level: (logging.LEVEL) Specifies the level to be logged.
        :param log_verbose: (boolean) Specifies whether or not to look to stdout as well.
        """
        self.logger = set_up_logger(__name__, log_file, log_level, log_verbose)
        self.window_size = window_size
        self.prefix = prefix + "_" + str(self.window_size)
        self.entities_only = entities_only
        self.names = self.get_names(self.prefix)
        self.port = port
        self.pc = PostgresConnector(port=port)
        self.logger.info("Successfully registered SchemaGenerator.")

    def get_names(self, prefix):
        names = []
        names.append(prefix + "_hyperedges")
        names.append(prefix + "_hyperedge_document")
        names.append(prefix + "_hyperedge_sentences")

        return names

    def create(self):
        """

        :return:
        """
        self.logger.info("Starting to create new {} hyperedge tables.".format(self.prefix))
        with self.pc as open_pc:
            # create hyperedge table
            if not check_table_existence(self.logger, open_pc, self.names[0]):
                self.logger.info("No hyperedge table found. Creating new one...")
                open_pc.cursor.execute("CREATE TABLE {} ( "
                                       "edge_id integer, "
                                       "term_id integer, "
                                       "pos integer, "
                                       "PRIMARY KEY (edge_id, term_id, pos), "
                                       "FOREIGN KEY (term_id) REFERENCES terms(term_id) ON DELETE CASCADE"
                                       ");".format(self.names[0]))

            if not check_table_existence(self.logger, open_pc, self.names[1]):
                self.logger.info("No hyperedge document table found. Creating new one...")
                open_pc.cursor.execute("CREATE TABLE {} ( "
                                       "edge_id integer, "
                                       "document_id integer, "
                                       "PRIMARY KEY (edge_id, document_id), "
                                       "FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE"
                                       ");".format(self.names[1]))

            if not check_table_existence(self.logger, open_pc, self.names[2]):
                self.logger.info("No hyperedge sentence table found. Creating new one...")
                open_pc.cursor.execute("CREATE TABLE {} ( "
                                       "edge_id integer, "
                                       "document_id integer, "
                                       "sentence_id integer, "
                                       "pos integer, "
                                       "PRIMARY KEY (edge_id, document_id, sentence_id, pos), "
                                       "FOREIGN KEY (document_id, sentence_id) "
                                       "REFERENCES sentences (document_id, sentence_id) "
                                       "ON DELETE CASCADE);".format(self.names[2]))

        hg = HyperedgeGenerator(entities_only=self.entities_only,
                                window_size=self.window_size,
                                hyperedge_table_name=self.names[0],
                                hyperedge_document_table_name=self.names[1],
                                hyperedge_sentence_table_name=self.names[2], port=self.port)
        hg.create_edges_naively()


if __name__ == "__main__":
    args = get_parser()
    print(args.prefix, args.window_size, args.entities_only)
    sys.stdout.flush()
    sc = SchemaCreator(prefix=args.prefix, window_size=args.window_size, entities_only=args.entities_only, port=args.port)
    sc.create()

