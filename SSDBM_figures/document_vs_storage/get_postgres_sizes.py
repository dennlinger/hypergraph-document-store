"""
Retrieves sizes of the different models for varying sizes.
"""

from PostgresConnector_SSDBM import PostgresConnector
import json


def get_sizes(vals, port):
    pc = PostgresConnector(port=port)

    create_remaining_indexes(pc)

    with pc as opc:
        opc.cursor.execute("SELECT COUNT(*)"
                           "FROM documents;")

        # has to contain .lower().startswith('execution time:')
        key = int(opc.cursor.fetchall()[0][0])

        size_query = """
        SELECT table_name, total_bytes FROM  (SELECT *, pg_size_pretty(total_bytes) AS total
                                    , pg_size_pretty(index_bytes) AS INDEX
                                    , pg_size_pretty(toast_bytes) AS toast
                                    , pg_size_pretty(table_bytes) AS TABLE
                                  FROM (
                                  SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
                                      SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
                                              , c.reltuples AS row_estimate
                                              , pg_total_relation_size(c.oid) AS total_bytes
                                              , pg_indexes_size(c.oid) AS index_bytes
                                              , pg_total_relation_size(reltoastrelid) AS toast_bytes
                                          FROM pg_class c
                                          LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                                          WHERE relkind = 'r' AND relname NOT LIKE 'pg_%'
                                  ) a
                                ) a) AS table_sizes ORDER BY total_bytes DESC;"""

        opc.cursor.execute(size_query)
        table_sizes = dict(opc.cursor.fetchall())  # list of tuples turned into dict

    # implicit: documents, sentences, terms, term_occurrence
    # explicit: documents, sentences, terms, hyperedges, hyperedge_document, hyperedge_sentences
    # epxlicit_entity: documents, sentences, terms, entity_hyperedges, entity_hyperedge_document, entity_hyperedge_sentences
    # explicit_dyadic: documents, sentences, terms, entity_dyadic, entity_hyperedge_document, entity_hyperedge_sentences

    implicit_size = sum_size(table_sizes, {"documents", "sentences", "terms", "term_occurrence"})
    explicit_size = sum_size(table_sizes, {"documents", "sentences", "terms", "hyperedges", "hyperedge_document",
                                           "hyperedge_sentences"})
    explicit_entity_size = sum_size(table_sizes, {"documents", "sentences", "terms", "entity_2_hyperedges",
                                                  "entity_2_hyperedge_document", "entity_2_hyperedge_sentences"})
    dyadic_entity_size = sum_size(table_sizes, {"documents", "sentences", "terms", "entity_2_dyadic",
                                                "entity_2_hyperedge_document", "entity_2_hyperedge_sentences"})

    vals[key] = {"implicit": implicit_size, "explicit": explicit_size, "explicit_entity": explicit_entity_size,
                 "dyadic_entity": dyadic_entity_size}

def create_remaining_indexes(pc):

    with pc as opc:
        opc.cursor.execute("CREATE INDEX entity_2_hyperedges_term_id ON public.entity_2_hyperedges "
                           "USING btree(term_id) WITH(fillfactor='100')")
        opc.cursor.execute("CREATE INDEX term_occurrence_term_id ON public.term_occurrence "
                           "USING btree (term_id) WITH (fillfactor='100')")
        opc.cursor.execute("CREATE INDEX entity_2_dyadic_source_id ON public.entity_2_dyadic USING btree (source_id)")


def sum_size(table_sizes, table_subset):
    result = 0
    for k, v in table_sizes.items():
        if k in table_subset:
            result += v
    return result


if __name__ == "__main__":

    ports = list(range(5435, 5440))
    # ports = [5435]
    sizes = {}
    for port in ports:
        get_sizes(sizes, port)

    with open("document_vs_storage.json", "w") as f:
        json.dump(sizes, f)
