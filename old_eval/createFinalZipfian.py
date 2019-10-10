import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


if __name__ == "__main__":

    data = pd.read_csv("../data/freq.csv", delimiter=",", header=None)

    y = data.iloc[:,1].values
    x = list(range(len(data)))

    ax = plt.gca()
    ax.plot(x,y)
    ax.set_xlim([-10,1000])
    ax.set_ylim([0,450000])
    ax.set_ylabel("# occurrences")
    ax.set_title("Frequency of Top 1000 Most Common Terms")
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.savefig("plots/zipfian.png")
    plt.show()