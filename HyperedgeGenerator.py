"""
Accesses a present document/term collection, and generates a neighborhood-based collection of hyperedges.
The idea is to perform only the least amount of operations on the actual machine, and try to generate the SQL
directly online.
Potentially, we iterate over every possible sentence, by having slightly overlapping "remembering parts".
What we mean by that is the fact that we can iteratively shift the window, as long as the results are in order.
"""

from PostgresConnector import PostgresConnector

from utils import set_up_logger, check_table_existence, insert_into_table

import logging
import os
import time


class HyperedgeGenerator:
    def __init__(self,
                 window_size=2,
                 limit_edges=False,
                 entities_only=False,
                 document_table_name="documents",
                 sentence_table_name="sentences",
                 entity_table_name="entities",
                 term_table_name="terms",
                 term_occurrence_table_name="term_occurrence",
                 hyperedge_table_name="hyperedges",
                 hyperedge_format=("edge_id", "term_id", "pos"),
                 hyperedge_document_table_name="hyperedge_document",
                 hyperedge_document_format=("edge_id", "document_id"),
                 hyperedge_sentence_table_name="hyperedge_sentences",
                 hyperedge_sentence_format=("edge_id", "document_id", "sentence_id", "pos"),
                 database="postgres",
                 user="postgres",
                 password="postgres",
                 host="127.0.0.1",
                 port=5435,
                 log_file=os.path.join(os.path.dirname(__file__), "logs/HyperedgeGenerator.log"),
                 log_level=logging.INFO,
                 log_verbose=True):
        """
        Initializes hyper edge generator class.
        :param window_size: (int) Number of sentences in each direction that will determine the context window size
               of the algorithm.
        :param limit_edges: (boolean) Experimental: Should limit the maximum number of terms per hyperedge. This would
               only be useful in context with other theoretical results.
        :param entities_only: (boolean) Indicating whether or not we should only take into account entity terms,
               and not the entirety of all term occurrences for the edges.
        :param document_table_name: (str) Name of the table where documents are stored.
        :param sentence_table_name: (str) Name of the table containing the sentences and their content.
        :param entity_table_name: (str) Name of the table containing the entity information and their properties.
        :param term_table_name: (str) Name of the table containing the terms and meta data.
        :param term_occurrence_table_name: (str) Name of the table containing term occurrence data.
        :param hyperedge_table_name: (str) Name of the table containing the general hyper edge information.
        :param hyperedge_format: (str) Table structure of hyper edge table.
        :param hyperedge_document_table_name: (str) Name of the table containing the document classification.
        :param hyperedge_document_format: (str) Table structure of hyper edge document table.
        :param hyperedge_sentence_table_name: (str) Name of the tale containing the hyper edge sentence data.
        :param hyperedge_sentence_format: (str) Table structure of the hyper edge sentence table.
        :param database: (str) database name.
        :param user: (str) User name to get access to the Postgres database.
        :param password: (str) Corresponding user password.
        :param host: (IP) IP address (in string format) for the host of the postgres database.
        :param port: (integer) Port at which to access the database.
        :param log_file: (os.path) Path to the file containing the logs.
        :param log_level: (logging.LEVEL) Specifies the level to be logged.
        :param log_verbose: (boolean) Specifies whether or not to look to stdout as well.
        """

        self.logger = set_up_logger(__name__, log_file, log_level, log_verbose)
        self.logger.info("Successfully registered logger to HyperedgeGenerator.")

        # important for hyperedges
        self.window_size = window_size
        self.limit_edges = limit_edges
        self.entities_only = entities_only

        # table names
        self.document_table_name = document_table_name
        self.sentence_table_name = sentence_table_name
        self.entity_table_name = entity_table_name
        self.term_table_name = term_table_name
        self.term_occurrence_table_name = term_occurrence_table_name
        self.hyperedge_table_name = hyperedge_table_name
        self.hyperedge_document_table_name = hyperedge_document_table_name
        self.hyperedge_sentence_table_name = hyperedge_sentence_table_name

        self.hyperedge_format = ", ".join([el for el in hyperedge_format])
        self.hyperedge_document_format = ", ".join([el for el in hyperedge_document_format])
        self.hyperedge_sentence_format = ",".join([el for el in hyperedge_sentence_format])

        self.pc = PostgresConnector(database, user, password, host, port)
        self.logger.info("Successfully registered PostgresConnector to HyperedgeGenerator.")

        self.hyperedge = []
        self.hyperedge_sentence = []
        self.hyperedge_document = []
        self.all_hyperedges = []
        self.all_hyperedge_sentences = []

        # set up the "hyper edge ID counter", which is simply consecutive from 1.
        with self.pc as open_pc:
            if not check_table_existence(self.logger, open_pc, self.hyperedge_table_name):
                return 0

            self.logger.info("Retrieving current hyper edge ID key...")
            open_pc.cursor.execute("SELECT COUNT(DISTINCT h.edge_id) FROM {} as h".format(self.hyperedge_table_name))
            # either start with 1 or get the current maximum
            self.hyperedge_ID = max(1, open_pc.cursor.fetchone()[0])

    def create_edges_naively(self):
        """
        Naively creates all the possible hyperedges, given the internally stored window size.
        :return: (None) Prepares the documents and stores them in class properties.
        """

        self.logger.info("Starting to generate hyperedges...")
        start_time = time.time()
        sentences = self.get_sentences()

        with self.pc as open_pc:
            # now create a hyperedge for every sentence
            for i, row in enumerate(sentences):
                # enable "batching"
                if i % int(len(sentences)/5) == 0 and i != 0:
                    self.logger.info("Done with {:.2f}% of hyperedges.".format(i*100 / len(sentences)))
                    self.insert_edges_naively(open_pc)

                self.generate_everything_from_sentence(row, open_pc)

            # final commit if something is left to commit.
            if self.hyperedge:
                self.logger.info("Done with {:.2f}% of hyperedges.".format(i * 100 / len(sentences)))
                self.insert_edges_naively(open_pc)

        end_time = time.time()
        self.logger.info("Successfully generated all hyper edges in {:.4f} s.".format(end_time - start_time))

    def get_sentences(self):
        """

        :return:
        """
        # iterate over every possible sentence
        with self.pc as open_pc:
            if not check_table_existence(self.logger, open_pc, self.sentence_table_name):
                return 0
            self.logger.info("Found {} table.".format(self.sentence_table_name))

            open_pc.cursor.execute("SELECT s.document_id, s.sentence_id FROM {} as s"
                                   .format(self.sentence_table_name))
            # TODO: Do we need the .fetchall() at all, or here, too?
            sentences = list(open_pc.cursor)

        return sentences

    def generate_everything_from_sentence(self, row, open_pc):
        """

        :param row:
        :param open_pc:
        :return:
        """
        # get all the different term occurrences:
        if not self.entities_only:
            query = "SELECT toc.term_id, toc.sentence_id - {} AS pos FROM {} as toc WHERE toc.document_id = {} " \
                    "AND toc.sentence_id BETWEEN {} AND {}" \
                    .format(row[1],
                            self.term_occurrence_table_name,
                            row[0],
                            row[1] - self.window_size,
                            row[1] + self.window_size)
        else:
            query = "SELECT toc.term_id, toc.sentence_id - {} AS pos FROM {} as toc, {} as t WHERE toc.document_id = {} " \
                    "AND toc.term_id = t.term_id AND t.is_entity = true AND toc.sentence_id BETWEEN {} AND {}" \
                    .format(row[1],
                            self.term_occurrence_table_name,
                            self.term_table_name,
                            row[0],
                            row[1] - self.window_size,
                            row[1] + self.window_size)
        open_pc.cursor.execute(query)

        self.hyperedge.append(set(open_pc.cursor.fetchall()))

        # generate all the participating sentences:
        open_pc.cursor.execute("SELECT DISTINCT sen.document_id, sen.sentence_id, sen.sentence_id - {} AS pos FROM {} as sen \
                                                WHERE sen.document_id = {} \
                                                AND sen.sentence_id BETWEEN {} AND {}"
                               .format(row[1],
                                       self.sentence_table_name,
                                       row[0],
                                       row[1] - self.window_size,
                                       row[1] + self.window_size))

        self.hyperedge_sentence.append(open_pc.cursor.fetchall())

        # since distance cannot span multiple documents, simply append a single document id.
        self.hyperedge_document.append(row[0])

    def insert_edges_naively(self, open_pc):
        """
        Take the naively created edges and insert them into the Postgres schema.
        :return: (None) Internally pushes to Postgres.w
        """

        start_time = time.time()
        self.logger.info("Starting to put edges into table...")
        # should this be done in the same with statement?
        if not (check_table_existence(self.logger, open_pc, self.hyperedge_table_name) and
                check_table_existence(self.logger, open_pc, self.hyperedge_sentence_table_name) and
                check_table_existence(self.logger, open_pc, self.hyperedge_document_table_name)):
            return 0
        self.logger.info("Found all relevant hyper edge tables.")

        # prepare data with index:
        self.prepare_data()

        self.insert_data(open_pc)

        # reset to save memory consumption!
        self.hyperedge = []
        self.all_hyperedges = []
        self.hyperedge_document = []
        self.hyperedge_sentence = []
        self.all_hyperedge_sentences = []

        end_time = time.time()
        self.logger.info("Successfully inserted all new hyper edges in {:.4f} s.".format(end_time - start_time))

    def prepare_data(self):
        for i, edge in enumerate(self.hyperedge):
            # TODO: Evaluate performance of list comprehension for each one of those, vs iteration like this
            self.hyperedge[i] = [(self.hyperedge_ID, el[0], el[1]) for el in edge]
            self.all_hyperedges.extend(self.hyperedge[i])
            self.hyperedge_document[i] = (self.hyperedge_ID, self.hyperedge_document[i])
            self.hyperedge_sentence[i] = [(self.hyperedge_ID, el[0], el[1], el[2]) for el in self.hyperedge_sentence[i]]
            self.all_hyperedge_sentences.extend(self.hyperedge_sentence[i])

            self.hyperedge_ID += 1

    def insert_data(self, open_pc):
        # start with the pure hyper edges
        insert_into_table(open_pc, self.hyperedge_table_name, self.hyperedge_format,
                          self.all_hyperedges, self.logger)

        # next are documents
        insert_into_table(open_pc, self.hyperedge_document_table_name, self.hyperedge_document_format,
                          self.hyperedge_document, self.logger)

        # and lastly the sentences
        insert_into_table(open_pc, self.hyperedge_sentence_table_name, self.hyperedge_sentence_format,
                          self.all_hyperedge_sentences, self.logger)

    def clear_table(self, table_name):
        """
        Deletes previously inserted values from the specified table.
        :param table_name: (str) Self-explanatory; Name of the table that should be cleared.
        :return: (None). Calls Postgres table with prepared DELETE-statement.
        """
        with self.pc as open_pc:
            if not check_table_existence(self.logger, open_pc, table_name):
                return 0
            self.logger.info("Found {} table.".format(table_name))

            self.logger.info("Deleting all previously inserted {}...".format(table_name))
            # Careful! This will remove ALL DATA!
            open_pc.cursor.execute("DELETE FROM {}".format(table_name))
            # TODO: Check whether document count is actually 0!
            self.logger.info("Successfully deleted all previously inserted {}.".format(table_name))

    def clear_all_tables(self):
        """
        Clears all the tables relevant for the hyper egdes.
        :return: (None)
        """
        self.clear_table(self.hyperedge_sentence_table_name)
        self.clear_table(self.hyperedge_document_table_name)
        self.clear_table(self.hyperedge_table_name)


if __name__ == "__main__":
    hg = HyperedgeGenerator()

    # hg.clear_all_tables()
    hg.create_edges_naively()
