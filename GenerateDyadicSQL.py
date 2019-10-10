"""
Generates a dyadic graph, but much faster and more efficient directly via SQL.
Assumes present entity and full graphs of different window sizes.
"""

from PostgresConnector import PostgresConnector
from psycopg2.errors import DuplicateTable

if __name__ == "__main__":

    ports = list(range(5435, 5440))
    for port in ports:
        pc = PostgresConnector(port=port)

        with pc as conn:
            conn.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema ='public'")

            tables = conn.cursor.fetchall()

        for table in tables:
            name = table[0]

            # check whether we have the right tables
            # (name.startswith("full_") or
            if name.startswith("entity_") and name.split("_")[1].isdigit() and name.endswith("hyperedges"):
            # if (name.startswith("full_1") or name.startswith("full_2")) and len(name.split("_")) == 3:
                print("Copying table {}.".format(name))
                dyadic_name = name.split("_")[0] + "_" + name.split("_")[1] + "_dyadic"
                query = """CREATE TABLE {} AS 
                                   (SELECT eh1.edge_id as edge_id, eh1.term_id as source_id, eh2.term_id as target_id, 
                                           ABS(eh1.pos - eh2.pos) AS pos
                                    FROM {} as eh1, {} as eh2
                                    WHERE eh1.edge_id = eh2.edge_id
                                    AND eh1.term_id != eh2.term_id)""".format(dyadic_name, name, name)
                print(query)
                index = """CREATE INDEX {}_edge_id ON public.{} USING btree (edge_id, source_id, target_id, pos)
                """.format(dyadic_name, dyadic_name)
                with pc as conn:
                    try:
                        conn.cursor.execute(query)
                    except DuplicateTable:
                        continue
                    try:
                        conn.cursor.execute(index)
                    except DuplicateTable:
                        continue

