"""
Create necessary tables (sentences_neo4j) in all postgres instances for later querying.
"""

import sys
import os

sys.path.append(os.path.abspath("./lib/"))
from PostgresConnector import PostgresConnector


def create_table(port):
    pc = PostgresConnector(port=port)

    with pc as opc:
        # add sentence index column but in separate table
        print("Starting with ")
        pc.cursor.execute("CREATE TABLE sentences_neo4j AS TABLE sentences;")
        pc.cursor.execute("ALTER TABLE sentences_neo4j ADD COLUMN id int;")
        pc.cursor.execute("""WITH numbered (sid, document_id, sentence_id) AS
                            (select row_number() OVER() sid, * from sentences_neo4j)
                            UPDATE sentences_neo4j
                            SET id = numbered.sid
                            FROM numbered
                            WHERE sentences_neo4j.document_id = numbered.document_id AND
                            sentences_neo4j.sentence_id = numbered.sentence_id;""")

        # add term_occurrence index
        print("Starting with term occurrences...")
        pc.cursor.execute("CREATE TABLE term_occurrence_neo4j AS TABLE term_occurrence;")
        pc.cursor.execute("ALTER TABLE term_occurrence_neo4j ADD COLUMN id int;")
        pc.cursor.execute("""WITH numbered (sid, document_id, sentence_id, term_id) AS
                            (select row_number() OVER() sid, * from term_occurrence)
                            UPDATE term_occurrence_neo4j
                            SET  id = numbered.sid                                                
                            FROM numbered
                            WHERE term_occurrence_neo4j.document_id = numbered.document_id AND
                            term_occurrence_neo4j.sentence_id = numbered.sentence_id AND
                            term_occurrence_neo4j.term_id = numbered.term_id;""")



if __name__ == "__main__":
    ports = list(range(5435, 5440))

    for port in ports:
        print("Starting with insertion on port {}.".format(port))
        create_table(port)