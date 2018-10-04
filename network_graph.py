import pandas as pd
import networkx
import matplotlib.pyplot as plt
import numpy
from sklearn.decomposition import PCA

df = pd.read_csv('top_100_relations.csv', index_col=0)

sig_df = df[df.sum(axis=1) > (df.sum(axis=1).mean() + df.sum(axis=1).std())]

sig_df = sig_df.drop(sig_df.sum(axis=1).sort_values(ascending=False).head(10).index.values)
sig_df = sig_df.drop(sig_df.sum(axis=0).sort_values(ascending=False).head(10).index.values, axis=1)

edges = []
sig_cols = []
weights = []
node_size = []
for column in list(sig_df):
    column_series = sig_df[column].sort_values(ascending=False).head(5)
    edges += [(column, i) for i in column_series.index.values]
    sig_cols += [i for i in column_series.index.values]
    weights += [i for i in (column_series / column_series.sum()).values]
    node_size.append(column_series.sum())
    # edges += [(column, i) for i in
    #           sig_df[sig_df[column] > (sig_df[column].mean() + sig_df[column].std())][column].index.values]
    # sig_cols += [i for i in
    #              sig_df[sig_df[column] > (sig_df[column].mean() + sig_df[column].std())][column].index.values]

print(edges)
print(sig_cols)
print(weights)
# .to_csv('top_100_pca.csv')
weights = [4 * i for i in weights]
node_max = sum(node_size)
node_size_normal = [0.02 * i for i in node_size]
# nodes = list(sig_df.index.values)
#
g = networkx.Graph()
g.add_nodes_from(list(set(sig_cols)))
g.add_nodes_from(list(sig_df))
g.add_edges_from(edges)
# print(g)
# networkx.draw_networkx_nodes(g, alpha=0.8)
networkx.draw_networkx(g, width=weights, node_size=node_size_normal, font_size=6,
                       edge_color='#96E6B3', node_color='#A3D9FF')
plt.show()
# print(nodes)/
