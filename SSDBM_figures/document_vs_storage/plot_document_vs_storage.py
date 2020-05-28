"""
Simple test plot for now
"""

import matplotlib.pyplot as plt
import matplotlib
import json


def y_getter(key, scaler=1024**2):
    return [0] + [v[key]/scaler for _, v in data.items()]


if __name__ == "__main__":

    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=16)
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)

    with open("document_vs_storage.json", "r") as f:
        data = json.load(f)
    # prepend 0, 0 to all values for "visual niceness"
    x = [0] + [int(key) for key in data.keys()]

    scaler = 1024**3
    y_implicit = y_getter("implicit", scaler)
    y_explicit = y_getter("explicit", scaler)
    y_explicit_entity = y_getter("explicit_entity", scaler)
    y_dyadic_entity = y_getter("dyadic_entity", scaler)

    y_implicit_neo4j = y_getter("implicit_neo4j", scaler)
    y_explicit_neo4j = y_getter("explicit_neo4j", scaler)
    y_explicit_entity_neo4j = y_getter("explicit_entity_neo4j", scaler)
    y_dyadic_entity_neo4j = y_getter("dyadic_entity_neo4j", scaler)


    # Three plot dimensions:
    # PSQL vs Neo4j: Marker
    # Dataset: line dotted or not
    # Model: Color
    plt.figure()
    plt.xlim([0, 120000])
    plt.xlabel("Number of documents")
    plt.ylabel("Storage size in GB")
    plt.ylim([0, 12.5])
    plt.plot(x, y_implicit, marker="o", color="#00996a", label="Implicit Full PSQL")
    plt.plot(x, y_explicit, marker="o", color="#460d80", label="Explicit Full PSQL")
    plt.plot(x, y_explicit_entity, marker="o", color="#460d80", linestyle="dashed", label="Explicit Entity PSQL")
    plt.plot(x, y_dyadic_entity, marker="o", color="#ffa82d", linestyle="dashed", label="Dyadic Entity PSQL")

    plt.plot(x, y_implicit_neo4j, marker="^", color="#00996a", label="Implicit Full Neo4j")
    plt.plot(x, y_explicit_neo4j, marker="^", color="#460d80", label="Explicit Full Neo4j")
    plt.plot(x, y_explicit_entity_neo4j, marker="^", color="#460d80", linestyle="dashed", label="Explicit Entity Neo4j")
    plt.plot(x, y_dyadic_entity_neo4j, marker="^", color="#ffa82d", linestyle="dashed", label="Dyadic Entity Neo4j")
    plt.xticks([0, 20000, 40000, 60000, 80000, 100000, 120000], ["0", "20k", "40k", "60k", "80k", "100k", "120k"])
    plt.legend()
    plt.savefig("document_vs_storage.pdf", dpi=300)
    plt.show()

