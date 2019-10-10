"""
Analysis of the dyadic projection for some relatively trivial SNA measures.
Described them in the BSC thesis.
"""

import igraph
import sys
import os
import numpy as np

# redirect prints to file.
# sys.stdout = open("./data/Analysis.txt", "w")

def getTopK(arr, vs, k=10):
    sort = [(y,x['name']) for y, x in sorted(zip(arr, vs), reverse=True)]
    return sort[:k]


def getMaxWeightedDegree(G):
    """
    Does the same as G.strength(weights=G.es["weight"]), before I figured out how it works exactly.
    :param G: (igraph.Graph) Graph object.
    :return: (None)
    """
    id = np.argmax(G.degree())
    deg = 0
    for pos in G.es.select(_source=id):
        deg += G.es["weight"][pos.index]
    for pos in G.es.select(_target=id):
        deg += G.es["weight"][pos.index]

    print("Maximum degree: {}".format(deg))


if __name__ == "__main__":
    # G = igraph.Graph.Read_Ncol("./data/test.csv",directed=False,weights=True)
    # folder = os.path.dirname(os.path.abspath(__file__))
    # fn = os.path.join(folder, "data/dyadic_edges.csv")
    fn = "../reduced.csv"
    G = igraph.Graph.Read_Ncol(fn, directed=False, weights=True)
    print(G.summary())
    print()

    print("Number of vertices: {}".format(G.vcount()))
    print("Number of edges: {}".format(G.ecount()))

    print()
    # get unweigted degree centrality:
    print("Average uweighted degree: {:.2f}".format(2*G.ecount()/G.vcount()))
    degrees = G.degree()
    print("Maximum unweighted degree: {}".format(max(degrees)))

    # weighted equivalent:
    strengths = G.strength(weights=G.es["weight"])
    print("Average weighted degree: {:.2f}".format(np.mean(strengths)))
    print("Maximum weighted degree: {:.0f}".format(max(strengths)))
    print()

    k = 50
    res_weighted = getTopK(strengths, G.vs, k=k)
    res_unweighted = getTopK(degrees, G.vs, k=k)
    # print(res_weighted)
    # print(res_unweighted)
    res_weighted = [el[1] for el in res_weighted]
    res_unweighted = [el[1] for el in res_unweighted]
    print("Number of same elements in Top {} degrees: {}".format(k, len(set(res_weighted).intersection(set(res_unweighted)))))

    avgcc = G.transitivity_avglocal_undirected()
    print("Average Local Clustering Coefficient: {:.4f}".format(avgcc))
    gcc = G.transitivity_undirected()
    print("Global Clustering Coefficient: {:.4f}".format(gcc))

    print()
    # Components and diameter
    comps = G.components()
    print("Number of components: {}".format(len(comps)))
    giant = comps.giant()
    print("Fraction of elements in giant component: {:.2f}%".format(100*giant.vcount()/G.vcount()))

    # diameter = giant.diameter() # 8
    # print("Diameter of giant component: {}".format(diameter))
    print("Diameter of giant component: 8")
    print()
    # assortativity
    assortativity = G.assortativity_degree()
    print("Assortativity Coefficient: {:.4f}".format(assortativity))

