"""
Visualize the aggregated results from all runs.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn
import json

if __name__ == "__main__":
    
    c0 = "#ffa82d"
    c1 = "#da893d"
    c2 = "#b56a4e"
    c5 = "#904b5e"
    c10 = "#6b2c6f"
    c20 = "#460d80"

    # # Reverse Order
    # c20 = "#ffa82d"
    # c10 = "#da893d"
    # c5 = "#b56a4e"
    # c2 = "#904b5e"
    # c1 = "#6b2c6f"
    # c0 = "#460d80"

    # # Reverse Order Alternative
    # c20 = "#ffa82d"
    # c10 = "#9ee525"
    # c5 = "#1dcc38"
    # c2 = "#17b2a8"
    # c1 = "#113899"
    # c0 = "#460d80"

    # # Alternative
    # c0 = "#ffa82d"
    # c1 = "#9ee525"
    # c2 = "#1dcc38"
    # c5 = "#17b2a8"
    # c10 = "#113899"
    # c20 = "#460d80"

    plt.rc('axes', titlesize=26)
    plt.rc('axes', labelsize=26)
    plt.rc('xtick', labelsize=24)
    plt.rc('ytick', labelsize=24)

    with open("entities.json") as f:
        data = json.load(f)

    row_names = list(data.keys())

    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["implicit"]["0"]),
                     np.mean(entity["implicit"]["1"]),
                     np.mean(entity["implicit"]["2"]),
                     np.mean(entity["implicit"]["5"]),
                     np.mean(entity["implicit"]["10"]),
                     np.mean(entity["implicit"]["20"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10", "time20"])
    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    seaborn.regplot("degree", "time20", df, ci=95, label="Window 20", marker=".", color=c20)
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.savefig("_deg_vs_time_implicit.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["explicit"]["0"]),
                     np.mean(entity["explicit"]["1"]),
                     np.mean(entity["explicit"]["2"]),
                     np.mean(entity["explicit"]["5"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.savefig("_deg_vs_time_explicit.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["implicit_entity"]["0"]),
                     np.mean(entity["implicit_entity"]["1"]),
                     np.mean(entity["implicit_entity"]["2"]),
                     np.mean(entity["implicit_entity"]["5"]),
                     np.mean(entity["implicit_entity"]["10"]),
                     np.mean(entity["implicit_entity"]["20"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10", "time20"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    seaborn.regplot("degree", "time20", df, ci=95, label="Window 20", marker=".", color=c20)
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.savefig("_deg_vs_time_implicit_entity.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["explicit_entity"]["0"]),
                     np.mean(entity["explicit_entity"]["1"]),
                     np.mean(entity["explicit_entity"]["2"]),
                     np.mean(entity["explicit_entity"]["5"]),
                     np.mean(entity["explicit_entity"]["10"]),
                     np.mean(entity["explicit_entity"]["20"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10", "time20"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    seaborn.regplot("degree", "time20", df, ci=95, label="Window 20", marker=".", color=c20)
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_explicit_entity.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["dyadic_entity"]["0"]),
                     np.mean(entity["dyadic_entity"]["1"]),
                     np.mean(entity["dyadic_entity"]["2"]),
                     np.mean(entity["dyadic_entity"]["5"]),
                     np.mean(entity["dyadic_entity"]["10"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    # plt.xlabel("Degree")
    plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.savefig("_deg_vs_time_dyadic_entity.png", dpi=300)
    plt.show()

    #####################
    # NEO4J
    #####################
    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["implicit_neo4j"]["0"]),
                     np.mean(entity["implicit_neo4j"]["1"]),
                     np.mean(entity["implicit_neo4j"]["2"]),
                     np.mean(entity["implicit_neo4j"]["5"]),
                     np.mean(entity["implicit_neo4j"]["10"]),
                     np.mean(entity["implicit_neo4j"]["20"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10", "time20"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    seaborn.regplot("degree", "time20", df, ci=95, label="Window 20", marker=".", color=c20)
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_implicit_neo4j.png", dpi=300)
    plt.show()

    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["explicit_neo4j"]["0"]),
                     np.mean(entity["explicit_neo4j"]["1"]),
                     np.mean(entity["explicit_neo4j"]["2"]),
                     np.mean(entity["explicit_neo4j"]["5"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_explicit_neo4j.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["implicit_entity_neo4j"]["0"]),
                     np.mean(entity["implicit_entity_neo4j"]["1"]),
                     np.mean(entity["implicit_entity_neo4j"]["2"]),
                     np.mean(entity["implicit_entity_neo4j"]["5"]),
                     np.mean(entity["implicit_entity_neo4j"]["10"]),
                     np.mean(entity["implicit_entity_neo4j"]["20"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10", "time20"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    seaborn.regplot("degree", "time20", df, ci=95, label="Window 20", marker=".", color=c20)
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_implicit_entity_neo4j.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["explicit_entity_neo4j"]["0"]),
                     np.mean(entity["explicit_entity_neo4j"]["1"]),
                     np.mean(entity["explicit_entity_neo4j"]["2"]),
                     np.mean(entity["explicit_entity_neo4j"]["5"]),
                     np.mean(entity["explicit_entity_neo4j"]["10"]),
                     np.mean(entity["explicit_entity_neo4j"]["20"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10", "time20"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    seaborn.regplot("degree", "time20", df, ci=95, label="Window 20", marker=".", color=c20)
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_explicit_entity_neo4j.png", dpi=300)
    plt.show()


    vals = []
    for name, entity in data.items():
        if entity["degree"] >= 10000:
            continue

        vals.append((entity["degree"],
                     np.mean(entity["dyadic_entity_neo4j"]["0"]),
                     np.mean(entity["dyadic_entity_neo4j"]["1"]),
                     np.mean(entity["dyadic_entity_neo4j"]["2"]),
                     np.mean(entity["dyadic_entity_neo4j"]["5"]),
                     np.mean(entity["dyadic_entity_neo4j"]["10"])))

    df = pd.DataFrame(vals, columns=["degree", "time0", "time1", "time2", "time5",
                                     "time10"])

    seaborn.regplot("degree", "time0", df, ci=95, label="Window 0", marker=".", color=c0)
    seaborn.regplot("degree", "time1", df, ci=95, label="Window 1", marker=".", color=c1)
    seaborn.regplot("degree", "time2", df, ci=95, label="Window 2", marker=".", color=c2)
    seaborn.regplot("degree", "time5", df, ci=95, label="Window 5", marker=".", color=c5)
    seaborn.regplot("degree", "time10", df, ci=95, label="Window 10", marker=".", color=c10)
    plt.xlabel("Degree")
    plt.ylabel("Execution time in ms")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.215, bottom=0.175, right=0.997, top=0.974)
    plt.savefig("_deg_vs_time_dyadic_entity_neo4j.png", dpi=300)
    plt.show()
