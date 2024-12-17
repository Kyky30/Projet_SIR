# utils.py
import matplotlib.pyplot as plt
import json
import os

VIRUS_DIR = 'virus'

def afficher_statistiques(statistiques, jour, ax_linear, ax_combined=None):
    """
    Affiche les statistiques de la simulation sur le graphique linéaire 2D.

    Args:
        statistiques (list): Liste des dictionnaires contenant les états de la population pour chaque jour.
        jour (int): Nombre de jours simulés.
        ax_linear (matplotlib.axes.Axes): Axes pour le graphique linéaire 2D.
        ax_combined (matplotlib.axes.Axes, optional): Axes pour le graphique combiné S, I, R, D. Defaults to None.
    """
    annees = range(1, jour + 1)
    sains = [etat['sains'] for etat in statistiques]
    contamines = [etat['contamines'] for etat in statistiques]
    infectes = [etat['infectes'] for etat in statistiques]
    retablis = [etat['retablis'] for etat in statistiques]
    morts = [etat['morts'] for etat in statistiques]

    # Graphique linéaire 2D
    ax_linear.clear()
    ax_linear.set_title("Évolution de la population")
    ax_linear.set_xlabel("Jour")
    ax_linear.set_ylabel("Nombre d'individus")
    ax_linear.plot(annees, sains, label='Sains', color='green')
    ax_linear.plot(annees, contamines, label='Contaminés', color='yellow')
    ax_linear.plot(annees, infectes, label='Infectés', color='red')
    ax_linear.plot(annees, retablis, label='Rétablis', color='blue')
    ax_linear.plot(annees, morts, label='Morts', color='black')
    ax_linear.legend()

    # Graphique combiné S, I, R, D pour vérification (optionnel)
    if ax_combined:
        ax_combined.clear()
        ax_combined.set_title("S, I, R, D - Évolution")
        ax_combined.set_xlabel("Jour")
        ax_combined.set_ylabel("Nombre d'individus")
        ax_combined.plot(annees, sains, label='Sains', color='green')
        ax_combined.plot(annees, infectes, label='Infectés', color='red')
        ax_combined.plot(annees, retablis, label='Rétablis', color='blue')
        ax_combined.plot(annees, morts, label='Morts', color='black')
        ax_combined.legend()

def save_virus(name, parameters):
    """
    Sauvegarde les paramètres d'un virus dans un fichier JSON.

    Args:
        name (str): Nom du virus.
        parameters (dict): Dictionnaire des paramètres du virus.
    """
    if not os.path.exists(VIRUS_DIR):
        os.makedirs(VIRUS_DIR)
    virus_path = os.path.join(VIRUS_DIR, f"{name}.json")
    with open(virus_path, 'w') as f:
        json.dump(parameters, f, indent=4)

def load_virus(name):
    """
    Charge les paramètres d'un virus à partir d'un fichier JSON.

    Args:
        name (str): Nom du virus.

    Returns:
        dict: Dictionnaire des paramètres du virus.

    Raises:
        FileNotFoundError: Si le fichier du virus n'existe pas.
    """
    virus_path = os.path.join(VIRUS_DIR, f"{name}.json")
    if not os.path.exists(virus_path):
        raise FileNotFoundError(f"Le fichier du virus '{name}' n'existe pas.")
    with open(virus_path, 'r') as f:
        parameters = json.load(f)
    return parameters

def list_viruses():
    """
    Liste tous les virus sauvegardés.

    Returns:
        list: Liste des noms des virus sauvegardés.
    """
    if not os.path.exists(VIRUS_DIR):
        os.makedirs(VIRUS_DIR)
    files = os.listdir(VIRUS_DIR)
    virus_names = [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
    return virus_names
