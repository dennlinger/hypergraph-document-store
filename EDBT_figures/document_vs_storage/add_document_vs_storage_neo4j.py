"""
Takes the existing document_vs_storage.json and adds the results for neo4j to it.
"""
import subprocess
import json
import os

def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du','-sb', path]).split()[0].decode('utf-8')


if __name__ == "__main__":
    with open("document_vs_storage.json", "r") as f:
        data = json.load(f)

    key_map = {"5435": "15523", "5436": "40467", "5437": "65467", "5438": "85827", "5439": "113312"}

    parent = "/data1/daumiller/hypergraphs-bp"
    subs = ["implicit_model", "explicit_model", "explicit_entity_model", "dyadic_model"]

    for sub in subs:
        for port in [str(el) for el in range(5435, 5440)]:
            folder = os.path.join(parent, sub, "graph_"+port+".db")

            graph_type = ""
            if sub == "implicit_model":
                graph_type = "implicit_neo4j"
            elif sub == "explicit_model":
                graph_type = "explicit_neo4j"
            elif sub == "explicit_entity_model":
                graph_type = "explicit_entity_neo4j"
            else:
                graph_type = "dyadic_entity_neo4j"
            data[key_map[port]][graph_type] = int(du(folder))

    with open("document_vs_storage.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

