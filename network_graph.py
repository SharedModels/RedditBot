import pandas as pd
import networkx
import matplotlib.pyplot as plt


class DrawNetworkGraph:
    def __init__(self, figure_size=(20, 10)):
        self.figure_size = figure_size
        self.edges = []
        self.sig_cols = []
        self.weights = []
        self.node_size = []

    def prepare_data(self, df):
        sig_df = df[df.sum(axis=1) > (df.sum(axis=1).mean() + df.sum(axis=1).std())]
        sig_df = sig_df.drop(sig_df.sum(axis=1).sort_values(ascending=False).head(10).index.values)
        sig_df = sig_df.drop(sig_df.sum(axis=0).sort_values(ascending=False).head(10).index.values, axis=1)
        return sig_df

    def prepare_graph(self, df):
        for column in list(df):
            column_series = df[column].sort_values(ascending=False).head(10)
            self.edges += [(column, i) for i in column_series.index.values]
            self.sig_cols += [i for i in column_series.index.values]
            self.weights += [i for i in (column_series / column_series.sum()).values]
            self.node_size.append(column_series.sum())
        self.weights = [5 * i for i in self.weights]

    def draw_graph(self, df):
        g = networkx.Graph()
        g.add_nodes_from(list(set(self.sig_cols)))
        g.add_nodes_from(list(df))
        g.add_edges_from(self.edges)
        # plt.figure(figsize=self.figure_size)

        networkx.draw_networkx(g, width=self.weights, font_size=6, node_size=50,
                               edge_color='#96E6B3', node_color='#A3D9FF')
        plt.axis('off')

    def save_graph(self, filename='reddit_dashboard/network_graph_full.png'):
        plt.savefig(filename)

    def dashboard_graph(self, df):
        df = self.prepare_data(df)
        self.prepare_graph(df)
        self.draw_graph(df)
        self.save_graph()
