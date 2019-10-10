import psycopg2 as db
import csv
import os
import sys
sys.path.append(os.path.abspath("../lib/"))
from query_helper import comm_helper
from PostgresConnector import PostgresConnector

# ports = list(range(5435, 5440))
port = 5436
windows = [5, 10]

t = comm_helper("postgres", "", "127.0.0.1", str(port))
pc = PostgresConnector(port=port)


def query_and_write(filename, query, header):
    with pc as opc:
        print("Start querying table {}".format(filename))
        if os.path.isfile(filename):
            os.remove(filename)
        opc.cursor.execute(query)
        # This only happens for documents

        print("Start writing table {}.".format(filename))
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)

            while True:
                data = opc.cursor.fetchmany(65536)
                if not data:
                    break
                csvwriter.writerows(data)

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

for window in windows:
# querying csv files for import
    print("Processing tables for window size {}.".format(window))

    query_and_write("edge_ids_{}.csv".format(window),
     "select distinct edge_id from entity_{}_hyperedge_sentences".format(window),
     ["edge_id:ID(Hyperedge)"])

    query_and_write("hyperedge_sentences_{}.csv".format(window),
    """select distinct sentences_neo4j.id, ehs.edge_id from entity_{}_hyperedge_sentences ehs, sentences_neo4j
    where ehs.document_id = sentences_neo4j.document_id and
    sentences_neo4j.sentence_id = ehs.sentence_id""".format(window),
    [":START_ID(Sentence)",":END_ID(Hyperedge)"])

    query_and_write("entity_hyperedge_document_{}.csv".format(window),
    "select document_id, edge_id from entity_{}_hyperedge_document".format(window),
    [":START_ID(Document)", ":END_ID(Hyperedge)"])

    query_and_write("term_in_term_{}.csv".format(window),
    "select edge_id, source_id, target_id, pos  from entity_{}_dyadic".format(window),
    ["edge_id:int", ":START_ID(Term)", ":END_ID(Term)", "pos"])

    # executing neo4j import
    os.system(
    """
neo4j-import --into graph_{}.db --id-type integer \
--multiline-fields=true \
--nodes:Document documents_{}.csv \
--nodes:Sentence sentences_{}.csv \
--nodes:Term terms_{}.csv  \
--nodes:Hyperedge edge_ids_{}.csv \
--relationships:S_IN_E hyperedge_sentences_{}.csv \
--relationships:E_IN_D entity_hyperedge_document_{}.csv \
--relationships:T_IN_T term_in_term_{}.csv \
    """.format(window, port, port, port, window, window, window, window)
    )
