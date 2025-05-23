import sys
from PyQt5 import QtWidgets, QtCore
from ui.ui_loader import load_ui
from max_flow_solver import solve_max_flow
from graph_visualization import GraphWidget


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(float, dict)
    error = QtCore.pyqtSignal(str)

    def __init__(self, edges, source, sink):
        super().__init__()
        self.edges = edges
        self.source = source
        self.sink = sink

    def run(self):
        try:
            max_flow, flows = solve_max_flow(self.edges, self.source, self.sink)
            self.finished.emit(max_flow, flows)
        except Exception as e:
            self.error.emit(str(e))


class MaxFlowApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        load_ui("ui/max_flow_gui.ui", self)
        self.setup_ui()
        self.thread = None
        self.edges = []

    def setup_ui(self):
        self.nodes = set()
        self.edges = []

        # Connexion des boutons
        self.btn_add_row.clicked.connect(self.add_table_row)
        self.btn_remove_row.clicked.connect(self.remove_table_row)
        self.btn_calculate.clicked.connect(self.solve_max_flow)
        self.table_edges.cellChanged.connect(self.update_nodes)

        # Création des widgets de graphe
        self.graph_widget = GraphWidget()
        self.result_graph_widget = GraphWidget()

        # Ajouter les widgets de graphe à l'interface
        self.tab_widget = QtWidgets.QTabWidget()
        self.centralwidget.layout().addWidget(self.tab_widget)

        # Créer une page pour les données
        self.data_widget = QtWidgets.QWidget()
        self.data_layout = QtWidgets.QVBoxLayout(self.data_widget)

        # Déplacer les widgets existants vers la page de données
        while self.centralwidget.layout().count():
            item = self.centralwidget.layout().takeAt(0)
            if item.widget():
                self.data_layout.addWidget(item.widget())

        # Ajouter les onglets
        self.tab_widget.addTab(self.data_widget, "Données")
        self.tab_widget.addTab(self.graph_widget, "Graphe")
        self.tab_widget.addTab(self.result_graph_widget, "Résultat")

        # Ajuster la taille de la fenêtre
        self.resize(800, 600)

    def add_table_row(self):
        row = self.table_edges.rowCount()
        self.table_edges.insertRow(row)

    def remove_table_row(self):
        row = self.table_edges.currentRow()
        if row >= 0:
            self.table_edges.removeRow(row)
            self.update_nodes()

    def update_nodes(self):
        self.nodes.clear()
        for row in range(self.table_edges.rowCount()):
            u = self.table_edges.item(row, 0).text() if self.table_edges.item(row, 0) else ""
            v = self.table_edges.item(row, 1).text() if self.table_edges.item(row, 1) else ""
            self.nodes.update([u, v])

        # Filtrer les chaînes vides
        self.nodes.discard("")

        self.cb_source.clear()
        self.cb_sink.clear()
        self.cb_source.addItems(sorted(self.nodes))
        self.cb_sink.addItems(sorted(self.nodes))

        # Mettre à jour le graphe
        self.update_graph()

    def get_edges(self):
        edges = []
        for row in range(self.table_edges.rowCount()):
            u_item = self.table_edges.item(row, 0)
            v_item = self.table_edges.item(row, 1)
            cap_item = self.table_edges.item(row, 2)

            u = u_item.text().strip() if u_item else ""
            v = v_item.text().strip() if v_item else ""
            cap = cap_item.text().strip() if cap_item else "0"

            # Vérifier si la capacité est un nombre valide
            if u and v and cap.isdigit():
                edges.append((u, v, int(cap)))
            elif u and v:
                # Si nous avons juste un problème avec la capacité, on l'affiche
                QtWidgets.QMessageBox.warning(self, "Erreur", f"Capacité invalide à la ligne {row + 1}")
        return edges

    def update_graph(self):
        """Mettre à jour le graphe avec les arêtes actuelles"""
        edges = self.get_edges()
        if edges:
            self.edges = edges  # Stocker les arêtes pour une utilisation ultérieure
            self.graph_widget.update_graph(edges, "Graphe du réseau")
            # Changer d'onglet pour montrer le graphe
            self.tab_widget.setCurrentIndex(1)

    def solve_max_flow(self):
        try:
            source = self.cb_source.currentText()
            sink = self.cb_sink.currentText()
            edges = self.get_edges()
            self.edges = edges  # Mettre à jour les arêtes stockées

            if not edges or not source or not sink:
                raise ValueError("Données incomplètes !")

            self.btn_calculate.setEnabled(False)
            self.thread = QtCore.QThread()
            self.worker = Worker(edges, source, sink)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_solution_found)
            self.worker.error.connect(self.on_solution_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.error.connect(self.thread.quit)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", str(e))
            self.btn_calculate.setEnabled(True)

    def on_solution_found(self, max_flow, flows):
        # Mettre à jour l'étiquette de résultat
        self.lbl_result.setText(f"Flot Maximal: {max_flow}")

        # Mettre à jour le tableau de résultats
        self.table_result.setRowCount(0)
        for (u, v), flow in flows.items():
            row = self.table_result.rowCount()
            self.table_result.insertRow(row)
            self.table_result.setItem(row, 0, QtWidgets.QTableWidgetItem(u))
            self.table_result.setItem(row, 1, QtWidgets.QTableWidgetItem(v))
            self.table_result.setItem(row, 2, QtWidgets.QTableWidgetItem(str(flow)))

        # Mettre à jour le graphe de résultat
        self.result_graph_widget.update_flow_graph(self.edges, flows, f"Flot Maximal: {max_flow}")

        # Changer d'onglet pour montrer le résultat
        self.tab_widget.setCurrentIndex(2)

        self.btn_calculate.setEnabled(True)

    def on_solution_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Erreur", message)
        self.btn_calculate.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MaxFlowApp()
    window.show()
    sys.exit(app.exec_())