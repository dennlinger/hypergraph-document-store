"""
Get sizes of the equivalent neo4j tables.
"""
from collections import defaultdict
import subprocess
import json
import os

def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return int(subprocess.check_output(['du','-sb', path]).split()[0].decode('utf-8'))


if __name__ == "__main__":
    fn = "./window_size_vs_storage.json"
    windows = [0, 1, 2, 5, 10, 20]
    if os.path.exists(fn):
        with open(fn) as f:
            vals = json.load(f)
    else:
        vals = defaultdict(lambda: dict())

    parent = "/data/daumiller/hypergraphs-bp/"
    # implicit
    for window in windows:
        vals[str(window)]["implicit_neo4j"] = du(os.path.join(parent, "implicit_model", "graph_5436.db"))

    # explicit (only up to 5)
    for window in windows[:4]:
        vals[str(window)]["explicit_neo4j"] = du(os.path.join(parent, "explicit_model", "graph_{}.db".format(window)))

    # explicit_entity
    for window in windows:
        vals[str(window)]["explicit_entity_neo4j"] = du(os.path.join(parent, "explicit_entity_model", "graph_{}.db".format(window)))

    # dyadic (up to 10)
    for window in windows[:5]:
        vals[str(window)]["dyadic_entity_neo4j"] = du(os.path.join(parent, "dyadic_model", "graph_{}.db".format(window)))

    with open(fn, "w", encoding="utf-8") as f:
        json.dump(vals, f, indent=2, ensure_ascii=False)

