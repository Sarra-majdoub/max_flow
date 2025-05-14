"""
Module pour charger les fichiers UI de PyQt5
"""
from PyQt5 import uic, QtWidgets

def load_ui(ui_file, widget_instance):
    """
    Charge un fichier UI de Qt Designer dans une instance de widget

    Args:
        ui_file (str): Chemin vers le fichier .ui
        widget_instance (QWidget): Instance de widget à charger

    Returns:
        bool: True si le chargement a réussi, False sinon
    """
    try:
        uic.loadUi(ui_file, widget_instance)
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier UI: {e}")
        return False