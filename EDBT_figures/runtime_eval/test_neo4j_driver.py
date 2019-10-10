"""
Test for neo4j driver
"""

import neo4j

def get_neighbors(tx, node):
    result = tx.run("PROFILE MATCH (q:Term)-[r:T_IN_E]-(e:Hyperedge) WHERE q.term_text = '{}' RETURN e;".format(node))

    # result = tx.run("profile MATCH(n) return n LIMIT 50;")
    # avail = result.summary().result_available_after
    return result


if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    driver = neo4j.GraphDatabase.driver(uri, auth=("neo4j", "H8a5l1l2o"))

    with driver.session() as session:
        res = session.write_transaction(get_neighbors, "Donald Trump")
        res.consume()
        print(res.summary().result_available_after)
