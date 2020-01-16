"""
Plot the results in a similar fashion to document-vs-storage.
"""

import matplotlib.pyplot as plt
import json

if __name__ == "__main__":

    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=16)
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)

    fn = "./window_size_vs_storage.json"
    with open(fn, "r") as f:
        data = json.load(f)
    x = [int(key) for key in data.keys()]

    scaler = 1024**3
    y_implicit = [v["implicit"]/scaler for _, v in data.items()]
    y_explicit = [v["explicit"]/scaler for k, v in data.items() if int(k) <= 10]
    y_explicit_entity = [v["explicit_entity"]/scaler for _, v in data.items()]
    y_dyadic_entity = [v["dyadic_entity"]/scaler for k, v in data.items() if int(k) <= 10]

    y_implicit_neo4j = [v["implicit_neo4j"]/scaler for _, v in data.items()]
    y_explicit_neo4j = [v["explicit_neo4j"]/scaler for k, v in data.items() if int(k) <= 10]
    y_explicit_entity_neo4j = [v["explicit_entity_neo4j"]/scaler for _, v in data.items()]
    y_dyadic_entity_neo4j = [v["dyadic_entity_neo4j"]/scaler for k, v in data.items() if int(k) <= 10]

    # Three plot dimensions:
    # PSQL vs Neo4j: Marker
    # Dataset: line dotted or not
    # Model: Color
    plt.figure()
    plt.xlim([-.4, 22])
    plt.xlabel("Window size")
    plt.ylabel("Storage size in GB")
    plt.ylim([1, 100])
    # plt.ylim(1, 80)
    plt.yscale("log")

    plt.plot(x, y_implicit, marker="o", color="#a6cee3", label="Implicit Full PSQL")
    plt.plot(x[:5], y_explicit, marker="o", color="#1f78b4", label="Explicit Full PSQL")
    plt.plot(x, y_explicit_entity, marker="o", color="#1f78b4", linestyle="dashed", label="Explicit Entity PSQL")
    plt.plot(x[:5], y_dyadic_entity, marker="o", color="#b2df8a", linestyle="dashed", label="Dyadic Entity PSQL")

    plt.plot(x, y_implicit_neo4j, marker="^", color="#a6cee3", label="Implicit Full Neo4j")
    plt.plot(x[:5], y_explicit_neo4j, marker="^", color="#1f78b4", label="Explicit Full Neo4j")
    plt.plot(x, y_explicit_entity_neo4j, marker="^", color="#1f78b4", linestyle="dashed", label="Explicit Entity Neo4j")
    plt.plot(x[:5], y_dyadic_entity_neo4j, marker="^", color="#b2df8a", linestyle="dashed", label="Dyadic Entity Neo4j")

    plt.xticks([0, 1, 2, 5, 10, 20])
    plt.legend(ncol=1)
    plt.savefig("window_size_vs_storage.pdf", dpi=300)
    plt.show()
