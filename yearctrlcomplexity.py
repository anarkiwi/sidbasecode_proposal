#!/usr/bin/env python

import glob
import pydot
import pandas as pd
import sys
from collections import Counter


year = sys.argv[1]


def ctrlbitlabels(state):
    state = int(state)
    labels = []
    for i, label in enumerate(
        ("GATE", "SYNC", "RING", "TEST", "TRI", "SAW", "PULSE", "NOISE"), start=0
    ):
        if 2**i & state:
            labels.append(label)
    if not labels:
        labels.append("0")
    return " ".join(labels)


df = pd.read_csv("/scratch/hvsc/sidinfo.csv")
df = df[df["released"].str.contains(year)]
zsts = []
for row in df.itertuples():
    path = str(row.path)
    path = path[: path.rfind(".sid")]
    path = f"/scratch/hvsc/{path}/*/*zst"
    zsts.extend(list(glob.glob(path)))

regs = [4, 11, 18]
edges = Counter()

for i, zst in enumerate(zsts):
    print(i, round(i / len(zsts) * 100, 2), zst)
    df = pd.read_csv(
        zst,
        header=None,
        names=["clock", "chip", "reg", "val"],
        sep=" ",
    )
    df = df[(df.reg == 4) | (df.reg == 11) | (df.reg == 18)]

    for reg in regs:
        edge_df = df[df["reg"] == reg][["val"]].copy()
        if not len(edge_df):
            continue
        edge_df["prev"] = edge_df["val"].shift(1).astype(pd.UInt64Dtype())
        for edge_pair, count in edge_df.value_counts().to_dict().items():
            edges[edge_pair] += count

total = sum(edges.values())
graph = pydot.Dot(
    graph_type="digraph", label=f"{year}: {len(edges)} unique transitions"
)
nodes = {}
for i, node_pair_count in enumerate(
    sorted(edges.items(), key=lambda x: x[1], reverse=True)
):
    node_pair, count = node_pair_count
    from_node, to_node = node_pair
    for node in (from_node, to_node):
        if node not in nodes:
            nodes[node] = pydot.Node(ctrlbitlabels(node))
    edge = pydot.Edge(nodes[from_node], nodes[to_node])
    edge.set_penwidth(max(int(count / total * 100), 1))
    graph.add_edge(edge)

graph.write_png(f"{year}.png")
