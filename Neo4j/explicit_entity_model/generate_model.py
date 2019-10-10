import psycopg2 as db
import csv
import os
import sys
sys.path.append(os.path.abspath("../lib/"))
from query_helper import comm_helper

# window = 2  # set as default. Previously, this was iterating over different window sizes, see ./unused/explicit_entity/
port = 5436
windows = [0, 1, 2, 5, 10, 20]
t = comm_helper("postgres", "", "127.0.0.1", str(port))
cursor = t.getCursor()

# These tables are the same across all window sizes.
t.query_and_write("documents_{}.csv".format(port),
                  "select * from documents",
                  ["document_id:ID(Document)", "title", "feedname", "category", "feedurl", "published:datetime"], 5)

t.query_and_write("terms_{}.csv".format(port),
                  "select * from terms",
                  ["term_id:ID(Term)", "term_text", "is_entity:boolean"])

t.query_and_write("sentences_{}.csv".format(port),
                  "select id, sentence_text from sentences_neo4j",
                  ["sentence_id:ID(Sentence)", "sentence_text"])

for window in windows:
# querying csv files for import
    print("Processing tables for window size {}.".format(window))

    print("Querying data")

    t.query_and_write("edge_id_{}.csv".format(window),
     "select distinct edge_id from entity_{}_hyperedge_sentences".format(window),
     ["edge_id:ID(Hyperedge)"])

    t.query_and_write("entity_hyperedges_{}.csv".format(window),
    """select term_id, edge_id, pos from entity_{}_hyperedges""".format(window),
    [":START_ID(Term)", ":END_ID(Hyperedge)", "pos"])

    t.query_and_write("hyperedge_sentences_{}.csv".format(window),
    """select distinct sentences_neo4j.id, ehs.edge_id from entity_{}_hyperedge_sentences ehs, sentences_neo4j
    where ehs.document_id = sentences_neo4j.document_id and
    sentences_neo4j.sentence_id = ehs.sentence_id""".format(window),
    [":START_ID(Sentence)",":END_ID(Hyperedge)"])

    t.query_and_write("entity_hyperedge_document_{}.csv".format(window),
    "select document_id, edge_id from entity_{}_hyperedge_document".format(window),
    [":START_ID(Document)", ":END_ID(Hyperedge)"])

    # executing neo4j import
    os.system(
    """
    neo4j-import --into graph_{}.db --id-type integer \
    --multiline-fields=true \
    --nodes:Document documents_{}.csv \
    --nodes:Sentence sentences_{}.csv \
    --nodes:Term terms_{}.csv  \
    --nodes:Hyperedge edge_id_{}.csv \
    --relationships:T_IN_E entity_hyperedges_{}.csv  \
    --relationships:S_IN_E hyperedge_sentences_{}.csv \
    --relationships:D_IN_E entity_hyperedge_document_{}.csv
    """.format(window, port, port, port, window, window, window, window)
        )

