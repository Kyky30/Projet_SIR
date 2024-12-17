# gui/main_window.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

class MainWindow:
    def __init__(self, root, simulation_app):
        self.root = root
        self.simulation_app = simulation_app
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Simulation de propagation")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        # Configuration du grid
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=0)  # Frame de contrôle
        self.root.columnconfigure(1, weight=1)  # Frame des graphiques
        
        # Frame des graphiques
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self.graph_frame.rowconfigure(0, weight=0)  # Toolbar
        self.graph_frame.rowconfigure(1, weight=1)  # Canvas
        self.graph_frame.columnconfigure(0, weight=1)
        
        # Création de la figure matplotlib
        self.fig = plt.Figure(figsize=(16, 9), tight_layout=True)
        self.ax_linear = self.fig.add_subplot(121)
        self.ax_linear.set_title("Évolution de la population")
        self.ax_linear.set_xlabel("Jour")
        self.ax_linear.set_ylabel("Nombre d'individus")
        
        self.ax_3d = self.fig.add_subplot(122, projection='3d')
        self.ax_3d.set_title("Diagramme de phase en 3D")
        self.ax_3d.set_xlabel("Sains")
        self.ax_3d.set_ylabel("Infectés")
        self.ax_3d.set_zlabel("Rétablis")
        
        # Sous-Frame pour la barre d'outils
        self.toolbar_frame = tk.Frame(self.graph_frame)
        self.toolbar_frame.grid(row=0, column=0, sticky='ew')
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky='nsew')
        
        # Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
    
    def update_graphs(self, statistiques):
        if not statistiques:
            return
        jours = range(1, len(statistiques) + 1)
        sains = [etat['sain'] for etat in statistiques]
        contamines = [etat['contaminé'] for etat in statistiques]
        infectes = [etat['infecté'] for etat in statistiques]
        retablis = [etat['rétabli'] for etat in statistiques]
        morts = [etat['mort'] for etat in statistiques]
        
        # Mise à jour du graphique linéaire 2D
        self.ax_linear.clear()
        self.ax_linear.set_title("Évolution de la population")
        self.ax_linear.set_xlabel("Jour")
        self.ax_linear.set_ylabel("Nombre d'individus")
        self.ax_linear.plot(jours, sains, label='Sains', color='green')
        self.ax_linear.plot(jours, contamines, label='Contaminés', color='yellow')
        self.ax_linear.plot(jours, infectes, label='Infectés', color='red')
        self.ax_linear.plot(jours, retablis, label='Rétablis', color='blue')
        self.ax_linear.plot(jours, morts, label='Morts', color='black')
        self.ax_linear.legend()
        
        # Mise à jour du diagramme de phase 3D
        self.ax_3d.clear()
        self.ax_3d.set_title("Diagramme de phase en 3D")
        self.ax_3d.set_xlabel("Sains")
        self.ax_3d.set_ylabel("Infectés")
        self.ax_3d.set_zlabel("Rétablis")
        self.ax_3d.plot(sains, infectes, retablis, color='purple', label='Trajectoire')
        self.ax_3d.scatter(sains[0], infectes[0], retablis[0], color='green', s=100, label='Début')
        self.ax_3d.scatter(sains[-1], infectes[-1], retablis[-1], color='red', s=100, label='Fin')
        self.ax_3d.legend()
        
        self.canvas.draw()
    
    def clear_graphs(self):
        # Réinitialiser les graphiques
        self.ax_linear.clear()
        self.ax_linear.set_title("Évolution de la population")
        self.ax_linear.set_xlabel("Jour")
        self.ax_linear.set_ylabel("Nombre d'individus")
        
        self.ax_3d.clear()
        self.ax_3d.set_title("Diagramme de phase en 3D")
        self.ax_3d.set_xlabel("Sains")
        self.ax_3d.set_ylabel("Infectés")
        self.ax_3d.set_zlabel("Rétablis")
        
        self.canvas.draw()
