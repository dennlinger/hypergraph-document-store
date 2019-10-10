"""
Generates the terms to be used in the graph.
Supposed goals:
- Retrieve raw sentences and decide how to process them
- Cross-reference with entities to get all valid terms
-
"""

import logging
import os
import spacy
import time

from collections import Counter, OrderedDict

from utils import set_up_logger, check_table_existence

from MongoConnector import MongoConnector
from PostgresConnector import PostgresConnector

from spacy.lang.en.stop_words import STOP_WORDS
from nltk.corpus import stopwords
from psycopg2 import ProgrammingError, IntegrityError
from psycopg2.extras import execute_values


class TermGenerator:
    def __init__(self,
                 num_distinct_documents=5000,
                 replace_entities=True,
                 max_term_length=127,
                 remove_stopwords=True,
                 custom_stopwords=[',', '.', '-', '\xa0', '“', '”', '"', '\n', '—', ':', '?', 'I', '(', ')'],
                 analyze=False,
                 document_tabe_name="documents",
                 sentence_table_name="sentences",
                 sentence_fields=OrderedDict({"doc_id":"document_id",
                                              "sen_id":"sentence_id",
                                              "content":"sentence_text"
                                             }),
                 term_table_name="terms",
                 term_sql_format=("term_id", "term_text", "is_entity"),
                 term_occurrence_table_name="term_occurrence",
                 term_occurrence_sql_format=("document_id","sentence_id","term_id"),
                 entity_table_name="entities",
                 entity_sql_format=("entity_id", "entity_type"),
                 database="postgres",
                 user="postgres",
                 password="postgres",
                 host="127.0.0.1",
                 port=5435,
                 log_file=os.path.join(os.path.dirname(__file__), "logs/TermGenerator.log"),
                 log_level=logging.INFO,
                 log_verbose=True):
        """
        Initializes various parameters, registers logger and MongoConnector, and sets up the limit.
        :param num_distinct_documents: (int) The number of distinct documents retrieved from the queries.
               For performance reasons, this should be limited during debugging/development.
               0 (Zero) represents no limit, in accordance with the MongoDB standard for .limit().
        :param replace_entities: (boolean) Whether or not the entities in the text should be replaced/recognised.
               The reason for this is that single terms might be merged together to one term, i.e. first and last name:
               "Dennis" "Aumiller" would be two separate terms in the traditional splitting (replace_entities=False),
               whereas - if set to true - "Dennis Aumiller" would represent only one entity.
        :param max_term_length: (int) Indicator of how long the terms are supposed to be (varchar property in table).
        :param remove_stopwords: (boolean) Determines whether or not stop words are removed. Currently, we are still
               deciding on the final set, but likely either one (or both) of NLTK and SpaCy's stop word lists.
        :param custom_stopwords: (list of strings) Additional words that will not be considered at adding-time.
        :param analyze: (boolean) Whether or not to include analytically relevant metrics.
        :param document_tabe_name: (str) Name of the table where the document information is stored.
        :param sentence_table_name: (str) Name of the table where the sentence information will be stored.
        :param sentence_fields: (OrderedDict) Structure of input to output values from MongoDB to postgres for the
               sentence table and its fields.
        :param term_table_name: (str) Name of the Postgres tables for the terms.
        :param term_sql_format: (tuple) Since those are generated locally, only a tuple of the PostgresColumns suffices.
        :param term_occurrence_table_name: (str) Name of the Postgres table for the term occurrences
        :param term_occurrence_sql_format: (tuple) Same as term_sql_format, but for the term occurrences.
        :param entity_table_name: (str) (Not implemented yet) Name of the table for the entity meta information.
        :param entity_sql_format: (str) Same as term_sql_format, but for entities.
        :param database: (str) database name.
        :param user: (str) User name to get access to the Postgres database.
        :param password: (str) Corresponding user password.
        :param host: (IP) IP address (in string format) for the host of the postgres database.
        :param port: (integer) Port at which to access the database.
        """
        # set up logger
        self.logger = set_up_logger(__name__, log_file, log_level, log_verbose)
        self.logger.info("Successfully registered logger to TermGenerator.")

        # register a MongoConnector
        self.mc = MongoConnector()
        self.logger.info("Successfully registered MongoConnector to TermGenerator.")

        # PostgresConnector
        self.pc = PostgresConnector(database, user, password, host, port)
        self.logger.info("Successfully registered PostgresConnector to DocumentGenerator.")

        self.num_distinct_documents = num_distinct_documents
        # do this earlier since we need it already for the distinct documents.
        self.document_table_name = document_tabe_name
        # get the distinct IDs for the documents so we can match against them later
        # since we have removed parts of the document collection, we have to make sure to get this from Postgres.
        self.logger.info("Parsing relevant documents from Postgres...")
        with self.pc as open_pc:
            open_pc.cursor.execute("SELECT document_id FROM {}".format(self.document_table_name))
            self.first_distinct_documents = list(open_pc.cursor.fetchall())
            # extract from the tuple structure
            self.first_distinct_documents = [el[0] for el in self.first_distinct_documents]
            self.logger.info("Retrieved all relevant documents from Postgres.")

        # additionally restrict if we want only a number of documents.
        if self.num_distinct_documents != 0:
            self.logger.info("Non-zero limit detected. Limiting to the first N entries.")
            self.first_distinct_documents = self.first_distinct_documents[:self.num_distinct_documents]

        self.replace_entities = replace_entities
        self.analyze = analyze

        self.max_term_length = max_term_length

        self.nlp = spacy.load("en")

        # construct dictionary with the entries per document/sentence id pair. Thus, we can later check whether
        # there are any entities in the current sentence with higher efficiency.
        self.occurrence_dict = {}
        self.occurring_entities = []

        # start building the term dictionary/set, as well as an occurence map. Since terms will be "post-processed",
        # it is first created as a list and later cast to Counter and set.
        self.terms = [] # cast into a set later on.
        self.term_in_sentence = set()
        self.term_id = {}
        self.term_is_entity = {}
        if self.analyze:
            self.term_count = Counter()
            self.entity_count = Counter()

        self.entities = []
        self.sentences = []
        self.processed_sentences = []

        # Postgres tables
        if not sentence_fields:
            self.logger.error("No sentence fields specified!")
        self.sentence_table_name = sentence_table_name
        self.sentence_fields = sentence_fields
        if not term_sql_format:
            self.logger.error("No term fields specified!")
        self.term_table_name = term_table_name
        self.term_sql_format = ", ".join(term_sql_format)
        if not term_occurrence_sql_format:
            self.logger.error("No term occurrence fields specified!")
        self.term_occurrence_table_name = term_occurrence_table_name
        self.term_occurrence_sql_format = ", ".join(term_occurrence_sql_format)
        if not entity_sql_format:
            self.logger.error("No entity fields specified!")
        self.entity_table_name = entity_table_name
        self.entity_sql_format = ", ".join(entity_sql_format)

        # value retrieving parse:
        self.sentence_values_to_retrieve = {key: 1 for key in self.sentence_fields.keys()}
        # suppress _id if not present:
        if "_id" not in self.sentence_values_to_retrieve.keys():
            self.sentence_values_to_retrieve["_id"] = 0
        self.sentence_sql_format = ", ".join([value for value in self.sentence_fields.values()])

        # create union of stop words, and add potentially custom stop words
        self.remove_stopwords = remove_stopwords
        self.removed_counter = 0
        self.stopwords = STOP_WORDS.union(set(stopwords.words("english")))
        # add custom stopwords.
        for word in custom_stopwords:
            self.stopwords.add(word)

        self.logger.info("Successfully initialized TermGenerator.")

    def get_relevant_documents_and_entities(self):
        """
        TODO!
        :return:
        """
        with self.mc as open_mc:
            sentences = open_mc.client[open_mc.news].sentences
            # distinction for (un)limited documents:
            if self.first_distinct_documents:
                self.sentences = list(sentences.find({"doc_id": {"$in": self.first_distinct_documents}},
                                                     self.sentence_values_to_retrieve))
            else:
                self.sentences = list(sentences.find({}, self.sentence_values_to_retrieve))

            # get entities only if we actually want to replace them.
            if self.replace_entities:
                self.replace_procedure(open_mc)

    def replace_procedure(self, open_mc):
        """
        TODO!
        :param open_mc:
        :return:
        """
        entities = open_mc.client[open_mc.news].entities
        # potentially RAM-hazardous for larger results:
        if self.first_distinct_documents:
            self.occurring_entities = list(entities.find({"doc_id": {"$in": self.first_distinct_documents}}))
        else:
            self.occurring_entities = list(entities.find({}))

        self.logger.info("Retrieved relevant entities. Found a total of {} occurrences.".
                         format(len(self.occurring_entities)))

        # do "blind pass" through the dict to collect all possible keys. The alternative is a single pass,
        # but requires a "for x in dict.keys()" check for every element, which is more costly,
        # especially for large results.
        for ent in self.occurring_entities:
            self.occurrence_dict[(ent["doc_id"], ent["sen_id"])] = []
        # now insert in the second pass
        for ent in self.occurring_entities:
            self.occurrence_dict[(ent["doc_id"], ent["sen_id"])].append(ent)

    def process_unreplaced(self):
        """
        TODO
        :return:
        """
        for doc in self.sentences:
            parsed = self.nlp(doc["content"], disable=['parser', 'tagger', 'ner'])

            for token in parsed:
                self.add_token(doc["doc_id"], doc["sen_id"], token.text, False)

    def process_replaced(self):
        """
        TODO!
        :return:
        """
        for doc in self.sentences:
            parsed = self.nlp(doc["content"], disable=['parser', 'tagger', 'ner'])

            # check whether there are any entities in the current sentence:
            try:
                self.process_document(doc, parsed)

            # no entities in the current sentence means we can "proceed as normal"
            except KeyError:
                for token in parsed:
                    self.add_token(doc["doc_id"], doc["sen_id"], token.text)

    def process_document(self, doc, parsed):
        """
        TODO!
        :param doc:
        :param parsed:
        :return:
        """
        # Get ascending order of elements
        current_entities = self.occurrence_dict[(doc["doc_id"], doc["sen_id"])]
        # Since they aren't quite sorted in ascending order within the document (sorting runs out of memory,
        # we have to "offline-sort" with respect to the starting position key.
        # This is probably also smarter, since we know that each sentence only has a very limited number of
        # entities, whereas the sort on the whole document collection is way way bigger. (Plus, we already
        # have some sort of sorting, and just need to have the last key.
        current_entities = sorted(current_entities, key=lambda k: k['start_sen'])

        current_el = current_entities.pop(0)
        # character position of start and end.
        current_start = current_el["start_sen"]
        current_end = current_el["end_sen"]
        # the last .pop() could be problematic. Avoid this with this boolean.
        reached_end = False

        for token in parsed:

            # before element to insert
            if token.idx < current_start or reached_end:
                self.add_token(doc["doc_id"], doc["sen_id"], token.text)

            # this means we hit the "coveredText" area.
            elif current_start <= token.idx < current_end:
                continue

            # we have covered all the entity, and now add the current_entity_text, as well as the next
            # element which was currently encountered (but to a separate entity)
            else:
                # also differentiate between dates and everything else.
                if current_el["neClass"] == "DAT":
                    current_entity_text = current_el["normalized"]
                else:
                    current_entity_text = current_el["normalized_label"]

                # add both the covered text, as well as the element that was not in it anymore
                self.add_token(doc["doc_id"], doc["sen_id"], current_entity_text,
                               True, current_el["neClass"])
                self.add_token(doc["doc_id"], doc["sen_id"], token.text)
                # reset entity elements. Be careful with popping, as the last element will still reach this.
                if current_entities:
                    current_el = current_entities.pop(0)
                    current_start = current_el["start_sen"]
                    current_end = current_el["end_sen"]

                else:
                    reached_end = True

    def postprocessing(self):
        """
        TODO
        :return:
        """
        # this allows us to later analyze the term frequency count.
        if self.analyze:
            self.term_count = Counter(self.terms)
            self.entity_count = Counter([el for el in self.terms if self.term_is_entity[el][0]])
        self.terms = set(self.terms)
        self.term_id = {term: i for i, term in enumerate(self.terms)}

        # get the corresponding entity information. Since term_id and entity_id have to match, we have to re-iterate
        self.entities = [(self.term_id[k], v[1]) for k, v in self.term_is_entity.items() if v[0]]

        # replace the words with the indexed term.
        self.term_in_sentence = [(el[0], el[1], self.term_id[el[2]]) for el in self.term_in_sentence]

        # "polish" the raw sentences as tuples that we can fit:
        self.sentences = [list(sent.values()) for sent in self.sentences]

    def parse(self):
        """
        Retrieves the data from the MongoDB, and locally matches entities (if enabled). Cleans them, and puts them into
        a term dictionary.
        :return: (None) Internally generates a list of terms, including their sentence and document position.
        """
        # open connection and retrieve sentences, as well as the corresponding occurring entities.
        self.logger.info("Starting to parse results...")
        start_time = time.time()

        self.get_relevant_documents_and_entities()

        # moved if to the outer part, since we'd otherwise do a re-check every iteration, even if it causes some
        # minor code duplication.
        self.logger.info("Starting to place parsed sentences in term dictionary...")
        if not self.replace_entities:
            self.process_unreplaced()

        else:
            self.process_replaced()

        self.postprocessing()

        self.logger.info("In total {} words were not inserted.".format(self.removed_counter))
        self.logger.info("Successfully parsed all relevant sentences.")
        end_time = time.time()
        self.logger.info("Total time taken for parsing results: {:.4f} s".format(end_time-start_time))

    def add_token(self, doc_id, sen_id, text, is_entity=False, entity_type=None):
        """
        Helper function that adds the given text to the set of terms, and term_in_sentence dictionary
        :param doc_id: (int) Document ID from the document containing the current sentence.
        :param sen_id: (int) Sentence position of the current sentence within the article it was processed from.
        :param text: (string) Text of the term to be appended.
        :param is_entity: (boolean) Indicator whether or not the entry is an entity
        :param entity_type: (string) If it is an entity, what entity class it belongs to.
        :return: None. Only internally adds the terms.
        """

        # if the word appears in the list of stopwords, don't add it.
        if self.remove_stopwords and text in self.stopwords:
            self.removed_counter += 1
            return None

        self.terms.append(text)
        # fill information on entity
        self.term_is_entity[text] = (is_entity, entity_type)

        # somehow fails if both of that is done in a single line.
        self.term_in_sentence.add((doc_id, sen_id, text))

    def push_sentences(self):
        """
        Puts the sentences in a Postgres table. Specifically in a separate function as this requires potentially less
        updates than the parsed terms.
        :return: (None) Internally puts up the documents in the Postgres table.
        """
        self.logger.info("Starting to push sentences in Postgres...")

        if not self.sentences:
            self.logger.error("No data found to be pushed! Please call .parse() first!")
            return 0

        with self.pc as open_pc:
            # TODO: Maybe check whether number of insertions matches feed.
            if not check_table_existence(self.logger, open_pc, self.sentence_table_name):
                return 0
            self.logger.info("Found sentence table.")

            self.logger.info("Inserting values.")

            # build query
            start_time = time.time()
            try:
                execute_values(open_pc.cursor,
                               "INSERT INTO {} ({}) VALUES %s".format(self.sentence_table_name, self.sentence_sql_format),
                               self.sentences)

                end_time = time.time()
                self.logger.info("Successfully inserted values in {:.4f} s".format(end_time - start_time))
            except IntegrityError as err:
                self.logger.error("Values with previously inserted primary key detected!\n {}".format(err))
                return 0

    def push_terms(self):
        """
        Puts the terms into a Postgres table.
        :return: (None) Internally pushes to Postgres.
        """

        self.logger.info("Starting to push terms into Postgres...")

        if not self.term_id:
            self.logger.error("No terms found to be pushed! Please call .parse() first!")
            return 0

        # prepare values for insertion. Also force length for test run.
        push_terms = [(val, key[:self.max_term_length], self.term_is_entity[key][0]) for key, val in self.term_id.items()]

        with self.pc as open_pc:
            # TODO: Maybe check whether number of insertions matches feed.
            if not check_table_existence(self.logger, open_pc, self.term_table_name):
                return 0
            self.logger.info("Found term table.")

            self.logger.info("Inserting values.")

            # build query
            start_time = time.time()
            try:
                execute_values(open_pc.cursor,
                               "INSERT INTO {} ({}) VALUES %s".format(self.term_table_name, self.term_sql_format),
                               push_terms)

                end_time = time.time()
                self.logger.info("Successfully inserted values in {:.4f} s".format(end_time - start_time))
            except IntegrityError as err:
                self.logger.error("Values with previously inserted primary key detected!\n {}".format(err))
                return 0

    def push_term_occurrences(self):
        """
        Puts the term occurrences into a Postgres table.
        :return: (None) Internally pushes to Postgres.
        """

        self.logger.info("Starting to push term occurrences into Postgres...")

        if not self.term_in_sentence:
            self.logger.error("No term occurrences found to be pushed! Please call .parse() first!")
            return 0

        with self.pc as open_pc:
            # TODO: Maybe check whether number of insertions matches feed.
            if not check_table_existence(self.logger, open_pc, self.term_occurrence_table_name):
                return 0
            self.logger.info("Found term table.")

            self.logger.info("Inserting values.")

            # build query
            start_time = time.time()
            try:
                execute_values(open_pc.cursor,
                               "INSERT INTO {} ({}) VALUES %s".format(self.term_occurrence_table_name,
                                                                      self.term_occurrence_sql_format),
                               self.term_in_sentence)

                end_time = time.time()
                self.logger.info("Successfully inserted values in {:.4f} s".format(end_time - start_time))
            except IntegrityError as err:
                self.logger.error("Values with previously inserted primary key detected!\n {}".format(err))
                return 0

    def push_entities(self):
        """
        Puts the entities into a Postgres table.
        :return: (None) Internally pushes to Postgres.
        """

        self.logger.info("Starting to push entities into Postgres...")

        if not self.entities:
            self.logger.error("No entities found to be pushed! Please call .parse() first!")
            return 0

        # prepare values for insertion. Also force length for test run.

        with self.pc as open_pc:
            # TODO: Maybe check whether number of insertions matches feed.
            if not check_table_existence(self.logger, open_pc, self.entity_table_name):
                return 0
            self.logger.info("Found entity table.")

            self.logger.info("Inserting values.")

            # build query
            start_time = time.time()
            try:
                execute_values(open_pc.cursor,
                               "INSERT INTO {} ({}) VALUES %s".format(self.entity_table_name, self.entity_sql_format),
                               self.entities)

                end_time = time.time()
                self.logger.info("Successfully inserted values in {:.4f} s".format(end_time - start_time))
            except IntegrityError as err:
                self.logger.error("Values with previously inserted primary key detected!\n {}".format(err))
                return 0

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


if __name__ == "__main__":

    tg = TermGenerator(num_distinct_documents=0)

    tg.parse()
    print([el for el in tg.terms if len(el) > 127])
    # print(tg.terms)
    # print("\n---------------------")
    # print(tg.sentences[0])
    # print("---------------------\n")
    # print(tg.term_in_sentence)
    # print(tg.term_id)
    # print(tg.term_count)
    tg.clear_table(tg.term_occurrence_table_name)
    tg.clear_table(tg.entity_table_name)
    tg.clear_table(tg.term_table_name)
    tg.clear_table(tg.sentence_table_name)
    tg.push_sentences()
    tg.push_terms()
    tg.push_entities()
    tg.push_term_occurrences()
