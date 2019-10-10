"""
Taken from the runtime evaluation, compare the results for dyadic queries and their hypergraph counterparts.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def compareFrequencyImpact(data, containerName):
    """
    Plot the different entities against one another, to see how frequency impacts performance.
    :param data: (np.array) Loaded runtime evaluation results.
    :param containerName: (str) Important for file output.
    :return: None.
    """
    relevantData = data[:, :21]
    yTrump = relevantData[:, :7]
    yJohnson = relevantData[:, 7:14]
    yDate = relevantData[:, 14:]
    xticks = ['co-oc exp ent', 'co-oc exp term', 'co-oc imp term', 'co-oc imp ent',
              'by week toc', 'by week exp term', 'by week exp ent']

    fig, ax = plt.subplots(figsize=(12,5))

    xPos = list(range(7))
    width = 0.25

    plotSubset(yTrump, xPos, width, "Donald Trump", 0)
    plotSubset(yJohnson, xPos, width, "Boris Johnson", 1)
    plotSubset(yDate, xPos, width, "2016-07-19", 2)
    ax.set_xticks([pos + 1 * width for pos in xPos])
    ax.set_xticklabels(xticks)
    plt.title("Query execution time for entities of different frequency")
    plt.ylabel("Query execution time in ms")
    plt.legend()
    plt.savefig("../data/queryRuntime{}.png".format(containerName))
    plt.show()


def compareHypergraphDyadic(data, containerName):
    """
    Compare the runtime of our subset of queries for dyadic vs hypergraphs.
    :param data: (np.array) Runtime evaluation results.
    :param containerName: (np.array) Important for file.
    :return: None
    """
    # see https://gitlab.com/dennis.aumiller/hyppograph/issues/60 for indices
    yHyper = data[:, [0, 6, 7, 13, 14, 20, 22, 25]]
    yDyadic = data[:, 31:]

    xticks = ['Trump co-oc', 'Trump by week', 'Johnson co-oc', 'Johnson co-oc',
              '07-19 co-oc', '07-19 by week', 'Date range occ', 'Degree count']
    fig, ax = plt.subplots(figsize=(12, 5))

    xPos = list(range(8))
    width = 0.25
    plotSubset(yHyper, xPos, width,"Hypergraph", 0)
    plotSubset(yDyadic, xPos, width, "Dyadic Reduction", 1)

    ax.set_xticks([pos + 0.5 * width for pos in xPos])
    ax.set_xticklabels(xticks)
    plt.title("Query execution time for hypergraph vs dyadic reduction")
    plt.ylabel("Query execution time in ms")
    plt.legend()
    plt.savefig("../data/hypergraphVsDyadic{}.png".format(containerName))
    plt.show()


def compareHypergraphDyadicImplicit(data, containerName):
    """
    Compare the runtime of our subset of queries for dyadic vs hypergraphs vs implicit equiv.
    Ignore last query due to bad performance overall (screws scale), and because there is so
    far no real equivalent.
    :param data: (np.array) Runtime evaluation results.
    :param containerName: (str) Important for file name.
    :return: None
    """
    # see https://gitlab.com/dennis.aumiller/hyppograph/issues/60 for indices
    yHyper = data[:, [0, 6, 7, 13, 14, 20, 22]]
    yDyadic = data[:, 31:38]
    yImplicit = data[:, [3, 4, 10, 11, 17, 18, 21]]

    xticks = ['Trump co-oc', 'Trump by week', 'Johnson co-oc', 'Johnson co-oc',
              '07-19 co-oc', '07-19 by week', 'Date range occ', 'Degree count']
    fig, ax = plt.subplots(figsize=(12, 5))

    xPos = list(range(7))
    width = 0.25
    plotSubset(yHyper, xPos, width,"Hypergraph", 0)
    plotSubset(yDyadic, xPos, width, "Dyadic Reduction", 1)
    plotSubset(yImplicit, xPos, width, "Implicit Equivalent", 2)

    ax.set_xticks([pos + 1 * width for pos in xPos])
    ax.set_xticklabels(xticks)
    plt.title("Query execution time for hypergraph vs dyadic reduction vs implicit graph")
    plt.ylabel("Query execution time in ms")
    plt.legend()
    plt.savefig("../data/hypergraphVsDyadicVsImplicit{}.png".format(containerName))
    plt.show()


def compareUnoptimizedOptimized(dataUnopt, dataOpt, containerUnopt, containerOpt):
    """
    Compare query runtimes between two different setups. Column dimensions must match.
    :param dataUnopt: (np.array)
    :param dataOpt: (np.array)
    :return: None
    """
    yUnopt = data[:, :31]
    yOpt = dataOpt[:, :31]
    xticks = ["Q"+str(i).zfill(2) for i in range(31)]
    fig, ax = plt.subplots(figsize=(20, 5))

    xPos = list(range(31))
    width = 0.25
    plotSubset(yUnopt, xPos, width, "Naive implementation", 0)
    plotSubset(yOpt, xPos, width, "Optimized implementation", 1)
    ax.set_xticks([pos + 0.5 * width for pos in xPos])
    ax.set_xticklabels(xticks)
    plt.title("Query execution time for naive implementation vs optimizations")
    plt.ylabel("Query execution time in ms")
    plt.legend()
    plt.savefig("../data/unoptimizedVsOptimized_{}_{}.png".format(containerUnopt, containerOpt))
    plt.show()


def compareIndividualUnoptimizedOptimized(dataUnopt, dataOpt):
    """
    Plots individual graphs for better visibility.
    :param dataUnopt: (np.array)
    :param dataOpt: (np.array)
    :return: None
    """

    pass


def plotSubset(subset, xPos, width,label, i):
    mean, median, std, minimum, maximum = analyzeData(subset)
    x = [pos + i*width for pos in xPos]
    plt.bar(x, mean, width, label=label, yerr=std)
    plt.scatter(x, minimum, color='r', marker='_')
    plt.scatter(x, maximum, color='r', marker='_')


def analyzeData(subset):
    mean = np.mean(subset, axis=0)
    median = np.median(subset, axis=0)
    std = np.std(subset, axis=0)
    min = np.min(subset, axis=0)
    max = np.max(subset, axis=0)

    return mean, median, std, min, max


if __name__ == "__main__":
    containerName = "hyppograph11_btree"
    data = pd.read_csv("../data/runtimeAnalysis_{}.txt".format(containerName),
                       sep=" ", header=None)
    data = data.values
    print(data.shape)
    
    # for output:
    compareFrequencyImpact(data, containerName)
    compareHypergraphDyadic(data, containerName)
    compareHypergraphDyadicImplicit(data, containerName)

    # load other dataset to get information.
    optContainerName = "hyppograph11_hash"
    dataOpt = pd.read_csv("../data/runtimeAnalysis_{}.txt".format(optContainerName),
                          sep=" ", header=None)
    dataOpt = dataOpt.values
    compareFrequencyImpact(dataOpt, optContainerName)
    compareHypergraphDyadic(dataOpt, optContainerName)
    compareHypergraphDyadicImplicit(dataOpt, optContainerName)

    # compare the two
    compareUnoptimizedOptimized(data, dataOpt, containerName, optContainerName)
