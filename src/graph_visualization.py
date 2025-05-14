import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from PyQt5 import QtWidgets


class NetworkVisualizer:
    def __init__(self):
        self.graph = nx.DiGraph()

    def create_graph(self, edges):
        """Créer un graphe orienté à partir d'une liste d'arêtes"""
        self.graph.clear()

        # Ajouter tous les arcs au graphe
        for u, v, capacity in edges:
            self.graph.add_edge(u, v, capacity=capacity, weight=capacity)

        return self.graph

    def create_flow_graph(self, edges, flows):
        """Créer un graphe montrant les flux"""
        self.graph.clear()

        # Ajouter tous les arcs au graphe avec leurs capacités et flux
        for u, v, capacity in edges:
            flow = flows.get((u, v), 0)
            self.graph.add_edge(u, v, capacity=capacity, flow=flow, weight=capacity)

        return self.graph

    def get_canvas(self, graph, title="Graphe de réseau", show_flows=False):
        """Créer un canevas Matplotlib avec le graphe visualisé"""
        fig = Figure(figsize=(6, 4), tight_layout=True)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Définir la disposition du graphe
        pos = nx.spring_layout(graph, seed=42)

        # Préparer les étiquettes des arêtes
        edge_labels = {}

        if show_flows:
            # Afficher "flux/capacité" sur chaque arc
            for u, v, data in graph.edges(data=True):
                edge_labels[(u, v)] = f"{data.get('flow', 0)}/{data['capacity']}"

            # Colorer les arêtes en fonction du ratio flux/capacité
            edge_colors = []
            for u, v, data in graph.edges(data=True):
                ratio = data.get('flow', 0) / data['capacity'] if data['capacity'] > 0 else 0
                edge_colors.append(plt.cm.viridis(ratio))

            nx.draw_networkx_edges(graph, pos, width=2, edge_color=edge_colors, ax=ax)
        else:
            # Afficher seulement les capacités
            for u, v, data in graph.edges(data=True):
                edge_labels[(u, v)] = str(data['capacity'])

            nx.draw_networkx_edges(graph, pos, width=2, ax=ax)

        # Dessiner les nœuds et les étiquettes
        nx.draw_networkx_nodes(graph, pos, node_size=700, node_color='lightblue', ax=ax)
        nx.draw_networkx_labels(graph, pos, font_weight='bold', ax=ax)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

        ax.set_title(title)
        ax.axis('off')

        return canvas


class GraphWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.visualizer = NetworkVisualizer()
        self.canvas = None

    def update_graph(self, edges, title="Graphe du réseau"):
        """Mettre à jour le graphe avec de nouvelles arêtes"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()

        graph = self.visualizer.create_graph(edges)
        self.canvas = self.visualizer.get_canvas(graph, title)
        self.layout.addWidget(self.canvas)

    def update_flow_graph(self, edges, flows, title="Flot maximal"):
        """Mettre à jour le graphe avec les résultats du flot"""
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()

        graph = self.visualizer.create_flow_graph(edges, flows)
        self.canvas = self.visualizer.get_canvas(graph, title, show_flows=True)
        self.layout.addWidget(self.canvas)