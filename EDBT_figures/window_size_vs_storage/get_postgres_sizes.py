"""
Get sizes from the postgres tables. Also has to create remaining missing indices.
"""

from PostgresConnector_EDBT import PostgresConnector
from collections import defaultdict
import psycopg2 as pg2
import json
import os


def get_sizes(vals, window):
    pc = PostgresConnector(port=5436)

    create_remaining_indexes(pc, window)

    with pc as opc:
        # basically just lists all tables and their sizes
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
    explicit_size = sum_size(table_sizes, {"documents", "sentences", "terms",
                                           "full_{}_hyperedges".format(window),
                                           "full_{}_hyperedge_document".format(window),
                                           "full_{}_hyperedge_sentences".format(window)})
    explicit_entity_size = sum_size(table_sizes, {"documents", "sentences", "terms",
                                                  "entity_{}_hyperedges".format(window),
                                                  "entity_{}_hyperedge_document".format(window),
                                                  "entity_{}_hyperedge_sentences".format(window)})
    dyadic_entity_size = sum_size(table_sizes, {"documents", "sentences", "terms",
                                                "entity_{}_dyadic".format(window),
                                                "entity_{}_hyperedge_document".format(window),
                                                "entity_{}_hyperedge_sentences".format(window)})

    vals[str(window)]["implicit"] = implicit_size
    vals[str(window)]["explicit_entity"] = explicit_entity_size
    if window <= 10:
        vals[str(window)]["dyadic_entity"] = dyadic_entity_size
        if window <= 5:
            vals[str(window)]["explicit"] = explicit_size

    print("Concluding window size {} operations.".format(window))

def create_remaining_indexes(pc, window):
    print("Creating indexes for window size {}".format(window))
    with pc as opc:
        try:
            opc.cursor.execute("CREATE INDEX entity_{}_hyperedges_term_id ON public.entity_{}_hyperedges "
                               "USING btree(term_id) WITH(fillfactor='100')".format(window, window))
        except pg2.ProgrammingError:
            pass

    with pc as opc:
        if window <= 10:
            try:
                opc.cursor.execute("CREATE INDEX entity_{}_dyadic_source_id ON public.entity_{}_dyadic "
                                   "USING btree(source_id) WITH(fillfactor='100')".format(window, window))
            except pg2.ProgrammingError:
                pass

    with pc as opc:
        if window <= 5:
            try:
                opc.cursor.execute("CREATE INDEX full_{}_hyperedges_term_id ON public.full_{}_hyperedges "
                                   "USING btree(term_id) WITH(fillfactor='100')".format(window, window))
            except pg2.ProgrammingError:
                pass


    print("Finished creating indexes for window size {}".format(window))


def sum_size(table_sizes, table_subset):
    result = 0
    for k, v in table_sizes.items():
        if k in table_subset:
            result += v
    return result


if __name__ == "__main__":
    windows = [0, 1, 2, 5, 10, 20]

    fn = "./window_size_vs_storage.json"
    if os.path.exists(fn):
        with open(fn) as f:
            vals = json.load(f)
    else:
        vals = defaultdict(lambda: dict())

    for window in windows:
        print("Starting with window size {}.".format(window))
        get_sizes(vals, window)

    with open(fn, "w", encoding="utf-8") as f:
        json.dump(vals, f, indent=2, ensure_ascii=False)
