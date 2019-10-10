"""
As the name indicates, generates a "simple" dyadic Graph based on the term co-occurrences.
We skip parts of the LOAD model, as for example the direct linking of sentences and documents, and instead
treat that part as "further available meta-information", but restrict our graph specifically to the terms, or respectively
entities.
"""

import numpy as np
import os

from PostgresConnector import PostgresConnector
from psycopg2 import IntegrityError
from psycopg2.extras import execute_values


def load_hyperedges(pc, table_name):
    """
    Returns the hyperedge list from the Postgres table.
    :param pc: (PostgresConnector) Object for communication.
    :param table_name: (string) Where to retrieve the values from
    :return: (list) Tuple values for (edge_id, term_id)
    """
    with pc as open_pc:
        open_pc.cursor.execute("SELECT * FROM {}".format(table_name))
        data = open_pc.cursor.fetchall()

    return data


def generate_dyadic_edges(hyperedges, pc, fn="./data/dyadic_edges.csv", batch_size=0):
    """
    Generates a dyadic edge list from a list of hyperedges.
    Note that this assumes the input hyperedges are in sorted order.
    :param hyperedges: (list) List of tuples with structure (edge_id, term_id).
    :param pc: (PostgresConnector) Used for inserting into postgres.
    :param fn: (string) File name for the edge_list
    :param batch_size: (int) If non-zero, after that many elements a file write will be executed, to make sure
           that not too much RAM will be used by the program.
    :return: ? Not sure yet
    """

    # convenience function, since 0 is easier to input.
    if batch_size == 0:
        batch_size = len(hyperedges)

    # touch file at the beginning to overwrite, since we are later appending
    # https://stackoverflow.com/questions/2769061/how-to-erase-the-file-contents-of-text-file-in-python
    open(fn, "w").close()

    # starting edge index
    curr_id = 1

    start_ind = 0
    end_ind = batch_size

    while start_ind < len(hyperedges):

        # avoid IndexError. This should only slightly increase the batch_size
        if not end_ind >= len(hyperedges):
            # correct break so that no edge gets split up by overlapping two batches.
            while hyperedges[end_ind][1] == hyperedges[end_ind+1][1]:
                end_ind += 1
                # further way to avoid error...
                if end_ind == len(hyperedges):
                    break

        edges, curr_id = handle_batch(hyperedges[start_ind:end_ind], curr_id)
        # append_edges(edges, fn)
        start_ind = end_ind
        end_ind += batch_size


def handle_batch(hyper_batch, curr_id):
    """
    What should be done within one iteration happens here.
    :param hyper_batch: (list) List of batch_size tuples of structure (edge_id, term_id)
    :param curr_id: (int) First identifier in this batch. Relevant if more than one batch to continue properly.
    :return: Returns list of generated dyadic edges
    """
    edge_dict = []
    postgres_dict = []
    expected_size = 0
    curr_hyperedge = []
    for i, edge in enumerate(hyper_batch):

        # edge is over. Actually append all the combinations.
        if curr_id != edge[0]:
            # generate
            edge_set, postgres_set = explode_hyperedge(curr_hyperedge, curr_id)
            edge_dict.extend(edge_set)
            postgres_dict.extend(postgres_set)
            expected_size += gaus(len(curr_hyperedge)-1)
            # also reset
            curr_id = edge[0]
            curr_hyperedge = [edge[1]]

        # just add this to the current hyperedge.
        else:
            curr_hyperedge.append(edge[1])

    if expected_size != len(edge_dict):
        raise ValueError("Size mismatch between theoretical prediction and actual length!")

    insert_edges(postgres_dict, pc)

    return edge_dict, curr_id


def explode_hyperedge(hyperedge, hyperedge_id):
    """
    Takes a hyperedge set, and generates all the dyadic connections for a similar regular edge.
    :param hyperedge: (list) List of participating terms.
    :param hyperedge_id: (int) Identifier for the hyperedge, used for postgres.
    :return: (list) List of connection tuples
    """

    # We'll sort, so we have a clear idea of how many of the same edge we have, since it will always be
    # of the form (smaller_id, larger_id).
    hyperedge = sorted(hyperedge)
    edge_set = []
    postgres_set = []
    # essentially build connections to all "vertices after". This guarantees we don't do edges twice.
    for i, _ in enumerate(hyperedge):
        for j in range(i+1, len(hyperedge)):
            edge_set.append((hyperedge[i], hyperedge[j]))
            # postgres performs better with duplicate edges, so we manually correct this here
            postgres_set.append((hyperedge_id, hyperedge[i], hyperedge[j]))
            postgres_set.append((hyperedge_id, hyperedge[j], hyperedge[i]))

    return edge_set, postgres_set


def insert_edges(postgres_set, pc, dyadic_table_name="entity_dyadic"):
    """
    Inserts a batch of dyadic edges into a postgres table.
    :param postgres_set: (list of tuples) Form of (id, source, target)
    :param pc: (PostgresConnector)
    :param dyadic_table_name: (str)
    :return: None
    """
    with pc as open_pc:
        if not check_table(open_pc, dyadic_table_name):
            open_pc.cursor.execute("CREATE TABLE {} ( edge_id integer, source_id integer, target_id integer, "
                                   "PRIMARY KEY (edge_id, source_id, target_id), "
                                   "FOREIGN KEY (source_id) REFERENCES terms (term_id),"
                                   "FOREIGN KEY (target_id) REFERENCES terms (term_id)"
                                   "ON DELETE CASCADE)".format(dyadic_table_name))

        try:
            execute_values(open_pc.cursor,
                           "INSERT INTO {} (edge_id, source_id, target_id) VALUES %s".format(dyadic_table_name),
                           postgres_set)

        except IntegrityError as err:
            print("Values with previously inserted primary key detected!\n {}".format(err))

    return 0


def check_table(connector, table_name):
    connector.cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables "
                             "WHERE table_name = %s);", (table_name,))

    return connector.cursor.fetchone()[0]


def gaus(n):
    return n * (n + 1) / 2


def append_edges(edges, fn):
    """
    Writes them to a file. Appending, since it is done in batches.
    :param edges: (list) list of edges, still including duplicates
    :param fn: (string) File name.
    :return: (None)
    """
    # TODO: This creates a bug!
    # edges = Counter(edges)
    # edges = np.array([(k[0], k[1], v) for k,v in edges.items()])

    edges = np.array(edges)

    with open(fn, "ab") as f:
        np.savetxt(f, edges, delimiter=" ", fmt="%i")


if __name__ == "__main__":
    pc = PostgresConnector(port=5436)
    hyperedges = load_hyperedges(pc, "entity_hyperedges")
    folder = os.path.dirname(os.path.abspath(__file__))
    fn = os.path.join(folder, "data/hyperedges_subset2.csv")
    generate_dyadic_edges(hyperedges, pc=pc, fn=fn, batch_size=50000)
    # hyperedges = load_hyperedges(pc, "entity_hyperedges")
    # generate_dyadic_edges(hyperedges, fn="./data/dyadic_edges.csv", batch_size=0)
