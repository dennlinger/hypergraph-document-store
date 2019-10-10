
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
    relevantData = data
    yTrump = relevantData[:, :3]
    yJohnson = relevantData[:, 3:6]
    yDate = relevantData[:, 6:]
    xticks = ['Implicit', 'Explicit Full', 'Explicit Entity-Only']

    fig, ax = plt.subplots(figsize=(12,5))

    xPos = list(range(3))
    width = 0.25

    plotSubset(yTrump, xPos, width, "Donald Trump", 0,u'#d62728')
    plotSubset(yJohnson, xPos, width, "Boris Johnson", 1, u'#9467bd')
    plotSubset(yDate, xPos, width, "2016-07-19", 2, u'#8c564b')
    ax.set_xticks([pos + 1 * width for pos in xPos])
    ax.set_xticklabels(xticks)
    plt.ylabel("Query execution time in ms")
    plt.legend()
    plt.savefig("q3runtime.png")
    plt.show()


def plotSubset(subset, xPos, width, label, i, c):
    mean, median, std, minimum, maximum = analyzeData(subset)
    x = [pos + i * width for pos in xPos]
    plt.bar(x, mean, width, label=label, color=c)
    plt.scatter(x, maximum, color='r', marker='_')


def analyzeData(subset):
    mean = np.mean(subset, axis=0)
    median = np.median(subset, axis=0)
    std = np.std(subset, axis=0)
    min = np.min(subset, axis=0)
    max = np.max(subset, axis=0)

    return mean, median, std, min, max


if __name__ == "__main__":

    data = pd.read_csv("intermediate.txt", sep=" ", header=None).values
    data2 = pd.read_csv("q3new.txt", sep=" ", header=None).values
    print(data.shape)
    print(data2.shape)

    samples = min(data.shape[0], data2.shape[0])
    cols = data.shape[1] + data2.shape[1]
    merged = np.zeros([samples, cols])
    merged[:,0] = data2[:samples, 0]
    merged[:,1:3] = data[:samples, 0:2]
    merged[:,3] = data2[:samples, 1]
    merged[:,4:6] = data[:samples, 2:4]
    merged[:, 6] = data2[:samples, 2]
    merged[:, 7:] = data[:samples, 4:]

    compareFrequencyImpact(merged, "dummy")