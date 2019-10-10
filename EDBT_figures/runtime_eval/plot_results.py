"""
Visualize the aggregated results from all runs.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn
import json

if __name__ == "__main__":

    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=16)
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)

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
    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    seaborn.regplot("degree", "time20", df, x_bins=bins, ci=95, label="Window 20", marker=".", color="#e31a1c")
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.savefig("_deg_vs_time_implicit.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.savefig("_deg_vs_time_explicit.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    seaborn.regplot("degree", "time20", df, x_bins=bins, ci=95, label="Window 20", marker=".", color="#e31a1c")
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.savefig("_deg_vs_time_implicit_entity.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    seaborn.regplot("degree", "time20", df, x_bins=bins, ci=95, label="Window 20", marker=".", color="#e31a1c")
    # plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_explicit_entity.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    # plt.xlabel("Degree")
    plt.ylabel("Execution time in ms")
    plt.xlabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.xticks([0, 1000, 2000, 3000, 4000, 5000, 6000], [])
    plt.savefig("_deg_vs_time_dyadic_entity.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    seaborn.regplot("degree", "time20", df, x_bins=bins, ci=95, label="Window 20", marker=".", color="#e31a1c")
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_implicit_neo4j.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_explicit_neo4j.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    seaborn.regplot("degree", "time20", df, x_bins=bins, ci=95, label="Window 20", marker=".", color="#e31a1c")
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_implicit_entity_neo4j.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    seaborn.regplot("degree", "time20", df, x_bins=bins, ci=95, label="Window 20", marker=".", color="#e31a1c")
    plt.xlabel("Degree")
    # plt.ylabel("Execution time in ms")
    plt.ylabel("")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000], [])
    plt.savefig("_deg_vs_time_explicit_entity_neo4j.pdf", dpi=300)
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

    bins = [1, 2, 3, 4, 5, 10, 20, 50, 80, 100, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    seaborn.regplot("degree", "time0", df, x_bins=bins, ci=95, label="Window 0", marker=".", color="#a6cee3")
    seaborn.regplot("degree", "time1", df, x_bins=bins, ci=95, label="Window 1", marker=".", color="#1f78b4")
    seaborn.regplot("degree", "time2", df, x_bins=bins, ci=95, label="Window 2", marker=".", color="#b2df8a")
    seaborn.regplot("degree", "time5", df, x_bins=bins, ci=95, label="Window 5", marker=".", color="#33a02c")
    seaborn.regplot("degree", "time10", df, x_bins=bins, ci=95, label="Window 10", marker=".", color="#fb9a99")
    plt.xlabel("Degree")
    plt.ylabel("Execution time in ms")
    plt.xlim([0, 6500])
    plt.ylim([0, 4000])
    # plt.legend(loc="upper left")
    plt.subplots_adjust(left=0.14, bottom=0.13, right=0.97, top=0.97)
    plt.savefig("_deg_vs_time_dyadic_entity_neo4j.pdf", dpi=300)
    plt.show()
