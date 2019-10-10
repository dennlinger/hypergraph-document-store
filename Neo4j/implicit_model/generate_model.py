import psycopg2 as db
import csv
import os
import sys

sys.path.append(os.path.abspath("../lib/"))
from query_helper import comm_helper


# ports = list(range(5435, 5440))
ports = [5436]
for port in ports:
# querying csv files for import
    print("Processing tables on port {}.".format(port))
    t = comm_helper("postgres", "", "127.0.0.1", str(port))
    cursor = t.getCursor()

    print("querying data")
    t.query_and_write("documents_{}.csv".format(port),
    "select * from documents",
    ["document_id:ID(Document)", "title", "feedname", "category", "feedurl", "published:datetime"], 5)

    t.query_and_write("terms_{}.csv".format(port),
    "select * from terms",
    ["term_id:ID(Term)", "term_text", "is_entity:boolean"])

    t.query_and_write("sentences_{}.csv".format(port),
     "select id, sentence_text from sentences_neo4j",
     ["sentence_id:ID(Sentence)", "sentence_text"])

    t.query_and_write("term_in_sentence_{}.csv".format(port),
    """
    select distinct toc.term_id, s.id from term_occurrence_neo4j toc, sentences_neo4j s
    where toc.sentence_id = s.sentence_id AND
    toc.document_id = s.document_id
    """,
    [":START_ID(Term)", ":END_ID(Sentence)"])

    t.query_and_write("sentence_in_document_{}.csv".format(port),
    """
    select distinct s.id, toc.document_id from term_occurrence toc, sentences_neo4j s
    where toc.sentence_id = s.sentence_id AND
    toc.document_id = s.document_id
    """,
    [":START_ID(Sentence)", ":END_ID(Document)"])

    t.query_and_write("term_in_document_{}.csv".format(port),
    """
    select distinct toc.term_id, toc.document_id from term_occurrence toc
    """,
    [":START_ID(Term)", ":END_ID(Document)"])

    # executing neo4j import
    print("Generating Neo4j table...")
    os.system(
    """
    neo4j-import --into graph_{}.db --id-type integer \
    --multiline-fields=true \
    --nodes:Term terms_{}.csv  \
    --nodes:Document documents_{}.csv  \
    --nodes:Sentence sentences_{}.csv  \
    --relationships:T_IN_S term_in_sentence_{}.csv  \
    --relationships:S_IN_D sentence_in_document_{}.csv  \
    --relationships:T_IN_D term_in_document_{}.csv 
    """.format(port, port, port, port, port, port, port)
    )
