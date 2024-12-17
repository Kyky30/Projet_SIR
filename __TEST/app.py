# app.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import json
import numpy as np
from scipy.integrate import odeint

# Gestion des fichiers de virus
VIRUS_DIR = 'virus'

def save_virus(name, parameters):
    if not os.path.exists(VIRUS_DIR):
        os.makedirs(VIRUS_DIR)
    virus_path = os.path.join(VIRUS_DIR, f"{name}.json")
    with open(virus_path, 'w') as f:
        json.dump(parameters, f, indent=4)

def load_virus(name):
    virus_path = os.path.join(VIRUS_DIR, f"{name}.json")
    if not os.path.exists(virus_path):
        raise FileNotFoundError(f"Le fichier du virus '{name}' n'existe pas.")
    with open(virus_path, 'r') as f:
        parameters = json.load(f)
    return parameters

def list_viruses():
    if not os.path.exists(VIRUS_DIR):
        os.makedirs(VIRUS_DIR)
    files = os.listdir(VIRUS_DIR)
    virus_names = [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
    return virus_names

# Modèle SEIR
def seir_model(y, t, beta, sigma, gamma, mu):
    S, E, I, R = y
    N = S + E + I + R
    dSdt = -beta * S * I / N
    dEdt = beta * S * I / N - sigma * E
    dIdt = sigma * E - gamma * I - mu * I
    dRdt = gamma * I
    return [dSdt, dEdt, dIdt, dRdt]

def simulate_seir(initial_sains, initial_contamines, initial_infectes, initial_retablis, initial_morts,
                 beta, sigma, gamma, mu, nombre_jours):
    # Conditions initiales
    S0 = initial_sains
    E0 = initial_contamines
    I0 = initial_infectes
    R0 = initial_retablis
    D0 = initial_morts
    y0 = [S0, E0, I0, R0]
    
    # Temps
    t = np.linspace(0, nombre_jours, nombre_jours)
    
    # Résolution des équations différentielles
    solution = odeint(seir_model, y0, t, args=(beta, sigma, gamma, mu))
    S, E, I, R = solution.T
    
    # Calcul des morts cumulés en intégrant mu * I
    D = D0 + np.cumsum(mu * I)  # Intégration cumulative
    
    # Compilation des résultats
    statistiques = []
    for day in range(nombre_jours):
        etats = {
            'sain': S[day],
            'contaminé': E[day],
            'infecté': I[day],
            'rétabli': R[day],
            'mort': D[day]
        }
        statistiques.append(etats)
    
    return statistiques

# Classe de l'application
class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.discretisation = tk.IntVar(value=10)  # Nombre de jours par itération
        
        # Paramètres de la vie
        self.initial_sains = tk.IntVar(value=9990)
        self.initial_contamines = tk.IntVar(value=0)
        self.initial_infectes = tk.IntVar(value=10)
        self.initial_retablis = tk.IntVar(value=0)
        self.initial_morts = tk.IntVar(value=0)
        
        # Paramètres du virus
        self.prob_contamination = tk.DoubleVar(value=0.15)  # Beta
        self.duree_incubation = tk.IntVar(value=3)          # Sigma inverse
        self.duree_infection = tk.IntVar(value=7)           # Gamma
        self.prob_vaccination = tk.DoubleVar(value=0.05)
        self.duree_immunite = tk.IntVar(value=30)
        self.taux_mortalite = tk.DoubleVar(value=0.02)      # Mu
        
        # Simulation
        self.nombre_jours = tk.IntVar(value=100)
        
        # Statistiques
        self.statistiques = []
        
        # Simulation state
        self.simulation_running = False
        self.current_jour = 0
        
        # Attribuer le module utils à self.utils
        self.utils = None  # Pas nécessaire dans ce fichier unique
        
        # Initialisation des composants GUI
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("Simulation de propagation")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        # Configuration du grid
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=0)  # Frame de contrôle
        self.root.columnconfigure(1, weight=1)  # Frame des graphiques
        
        # Frame de contrôle
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.control_frame.columnconfigure(0, weight=1)
        
        self.setup_control_panel()
        
        # Frame des graphiques
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self.graph_frame.rowconfigure(0, weight=0)  # Toolbar
        self.graph_frame.rowconfigure(1, weight=1)  # Canvas
        self.graph_frame.columnconfigure(0, weight=1)
        
        self.setup_graphs()
        
        # Mettre à jour les paramètres affichés après initialisation complète
        self.mettre_a_jour_label_parametres()
    
    def setup_control_panel(self):
        # Boutons de contrôle
        tk.Button(self.control_frame, text="Lancer la simulation", command=self.lancer_simulation)\
            .grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.control_frame, text="Arrêter la simulation", command=self.arreter_simulation)\
            .grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.control_frame, text="Réinitialiser", command=self.reinitialiser_simulation)\
            .grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.control_frame, text="Modifier les paramètres", command=self.ouvrir_fenetre_parametres)\
            .grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.control_frame, text="Quitter", command=self.quitter_simulation)\
            .grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Affichage des paramètres
        tk.Label(self.control_frame, text="Paramètres actuels:", font=("Helvetica", 10, "bold"))\
            .grid(row=5, column=0, columnspan=2, pady=(10, 0))
        self.label_parametres = tk.Label(self.control_frame, text="", justify="left")
        self.label_parametres.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky='ew')
        
        # Gestion des virus
        tk.Label(self.control_frame, text="Gestion des virus:", font=("Helvetica", 10, "bold"))\
            .grid(row=7, column=0, columnspan=2, pady=(10, 0))
        tk.Button(self.control_frame, text="Sauvegarder comme Virus", command=self.sauvegarder_comme_virus)\
            .grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        tk.Label(self.control_frame, text="Charger un Virus:").grid(row=9, column=0, padx=5, pady=5, sticky='e')
        self.virus_selection = tk.StringVar()
        self.virus_list = list_viruses()
        options = self.virus_list if self.virus_list else ['Aucun']
        self.virus_selection.set(options[0] if options else 'Aucun')
        self.dropdown_virus = tk.OptionMenu(self.control_frame, self.virus_selection, *options)
        self.dropdown_virus.grid(row=9, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Button(self.control_frame, text="Charger Virus", command=self.charger_virus)\
            .grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        tk.Button(self.control_frame, text="Supprimer Virus", command=self.supprimer_virus)\
            .grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Discrétisation
        tk.Label(self.control_frame, text="Discrétisation (jours):").grid(row=12, column=0, padx=5, pady=5, sticky='e')
        self.entry_discretisation = tk.Entry(self.control_frame, textvariable=self.discretisation)
        self.entry_discretisation.grid(row=12, column=1, padx=5, pady=5, sticky='w')
        
        # Espacement flexible
        tk.Label(self.control_frame).grid(row=15, column=0, columnspan=2, pady=10)
    
    def setup_graphs(self):
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
    
    def mettre_a_jour_label_parametres(self):
        # Mettre à jour l'affichage des paramètres
        texte = (
            f"--- Paramètres de la Vie ---\n"
            f"Nombre de sains: {self.initial_sains.get()}\n"
            f"Nombre de contaminés: {self.initial_contamines.get()}\n"
            f"Nombre d'infectés: {self.initial_infectes.get()}\n"
            f"Nombre de rétablis: {self.initial_retablis.get()}\n"
            f"Nombre de morts: {self.initial_morts.get()}\n\n"
            f"--- Paramètres du Virus ---\n"
            f"Probabilité de contamination (Beta): {self.prob_contamination.get() * 100}%\n"
            f"Durée d'incubation (1/Sigma): {self.duree_incubation.get()} jours\n"
            f"Durée d'infection (Gamma): {self.duree_infection.get()} jours\n\n"
            f"--- Paramètres de la Rétablissement ---\n"
            f"Probabilité de vaccination: {self.prob_vaccination.get() * 100}%\n"
            f"Durée d'immunité: {self.duree_immunite.get()} jours\n\n"
            f"--- Paramètres de la Mortalité ---\n"
            f"Taux de mortalité (Mu): {self.taux_mortalite.get() * 100}%\n\n"
            f"Nombre de jours de simulation: {self.nombre_jours.get()}\n"
            f"Discrétisation (jours): {self.discretisation.get()}"
        )
        self.label_parametres.config(text=texte)
    
    def ouvrir_fenetre_parametres(self):
        ParameterWindow(self.root, self)
    
    def lancer_simulation(self):
        if not self.simulation_running:
            # Récupérer les paramètres
            S0 = self.initial_sains.get()
            E0 = self.initial_contamines.get()
            I0 = self.initial_infectes.get()
            R0 = self.initial_retablis.get()
            D0 = self.initial_morts.get()
            beta = self.prob_contamination.get()
            sigma = 1 / self.duree_incubation.get() if self.duree_incubation.get() != 0 else 0
            gamma = 1 / self.duree_infection.get() if self.duree_infection.get() != 0 else 0
            mu = self.taux_mortalite.get()
            nombre_jours = self.nombre_jours.get()
            discretisation = self.discretisation.get()
            
            # Validation des paramètres
            total_population = S0 + E0 + I0 + R0 + D0
            if total_population > 10000:
                messagebox.showerror("Erreur", "La population totale ne doit pas dépasser 10 000 individus.")
                return
            if not (0 <= beta <= 1):
                messagebox.showerror("Erreur", "La probabilité de contamination (Beta) doit être entre 0 et 1.")
                return
            if sigma < 0 or gamma < 0 or mu < 0:
                messagebox.showerror("Erreur", "Les taux Sigma, Gamma et Mu doivent être positifs.")
                return
            if nombre_jours <= 0:
                messagebox.showerror("Erreur", "Le nombre de jours de simulation doit être un nombre positif.")
                return
            if discretisation <= 0:
                messagebox.showerror("Erreur", "La discrétisation doit être un nombre positif.")
                return
            
            # Lancer la simulation
            self.simulation_running = True
            self.current_jour = 0
            self.statistiques = []
            self.simuler_jour(beta, sigma, gamma, mu, nombre_jours, discretisation)
        else:
            messagebox.showinfo("Info", "Simulation déjà en cours")
    
    def simuler_jour(self, beta, sigma, gamma, mu, nombre_jours, discretisation):
        if self.simulation_running and self.current_jour < nombre_jours:
            jours_a_simuler = min(discretisation, nombre_jours - self.current_jour)
            # Effectuer la simulation SEIR pour le bloc de jours
            statistiques = simulate_seir(
                initial_sains=self.initial_sains.get(),
                initial_contamines=self.initial_contamines.get(),
                initial_infectes=self.initial_infectes.get(),
                initial_retablis=self.initial_retablis.get(),
                initial_morts=self.initial_morts.get(),
                beta=beta,
                sigma=sigma,
                gamma=gamma,
                mu=mu,
                nombre_jours=jours_a_simuler
            )
            self.statistiques.extend(statistiques)
            self.current_jour += jours_a_simuler
            print(f"Jours {self.current_jour - jours_a_simuler +1} à {self.current_jour}: {statistiques}")
            
            # Mise à jour des graphiques
            self.update_graphs()
            
            # Planifier le prochain bloc de jours
            self.root.after(100, lambda: self.simuler_jour(beta, sigma, gamma, mu, nombre_jours, discretisation))
        else:
            self.simulation_running = False
            self.mettre_a_jour_label_parametres()
            messagebox.showinfo("Info", "Simulation terminée")
    
    def arreter_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
            messagebox.showinfo("Info", "Simulation arrêtée")
        else:
            messagebox.showinfo("Info", "Aucune simulation en cours")
    
    def reinitialiser_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
        self.statistiques = []
        self.current_jour = 0
        self.clear_graphs()
        self.mettre_a_jour_label_parametres()
        messagebox.showinfo("Info", "Simulation réinitialisée")
    
    def sauvegarder_comme_virus(self):
        nom_virus = simpledialog.askstring("Nom du Virus", "Entrez le nom du virus:")
        if not nom_virus:
            messagebox.showwarning("Avertissement", "Le nom du virus ne peut pas être vide.")
            return
        if nom_virus in list_viruses():
            overwrite = messagebox.askyesno("Confirmation", f"Le virus '{nom_virus}' existe déjà. Voulez-vous le remplacer?")
            if not overwrite:
                return
        # Préparer les paramètres
        parameters = {
            'initial_sains': self.initial_sains.get(),
            'initial_contamines': self.initial_contamines.get(),
            'initial_infectes': self.initial_infectes.get(),
            'initial_retablis': self.initial_retablis.get(),
            'initial_morts': self.initial_morts.get(),
            'prob_contamination': self.prob_contamination.get(),
            'duree_incubation': self.duree_incubation.get(),
            'duree_infection': self.duree_infection.get(),
            'prob_vaccination': self.prob_vaccination.get(),
            'duree_immunite': self.duree_immunite.get(),
            'taux_mortalite': self.taux_mortalite.get(),
            'nombre_jours': self.nombre_jours.get(),
            'discretisation': self.discretisation.get()
        }
        try:
            save_virus(nom_virus, parameters)
            messagebox.showinfo("Info", f"Virus '{nom_virus}' sauvegardé avec succès.")
            self.update_virus_dropdown()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde du virus: {e}")
    
    def charger_virus(self):
        nom_virus = self.virus_selection.get()
        if nom_virus == 'Aucun' or not nom_virus:
            messagebox.showwarning("Avertissement", "Aucun virus sélectionné.")
            return
        try:
            parameters = load_virus(nom_virus)
            # Appliquer les paramètres
            self.initial_sains.set(parameters['initial_sains'])
            self.initial_contamines.set(parameters['initial_contamines'])
            self.initial_infectes.set(parameters['initial_infectes'])
            self.initial_retablis.set(parameters['initial_retablis'])
            self.initial_morts.set(parameters.get('initial_morts', 0))
            self.prob_contamination.set(parameters['prob_contamination'])
            self.duree_incubation.set(parameters['duree_incubation'])
            self.duree_infection.set(parameters['duree_infection'])
            self.prob_vaccination.set(parameters['prob_vaccination'])
            self.duree_immunite.set(parameters['duree_immunite'])
            self.taux_mortalite.set(parameters['taux_mortalite'])
            self.nombre_jours.set(parameters['nombre_jours'])
            self.discretisation.set(parameters.get('discretisation', 10))
            # Mise à jour des labels et graphiques
            self.mettre_a_jour_label_parametres()
            self.update_graphs()
            messagebox.showinfo("Info", f"Virus '{nom_virus}' chargé avec succès.")
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Le virus '{nom_virus}' n'a pas été trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du virus: {e}")
    
    def supprimer_virus(self):
        nom_virus = self.virus_selection.get()
        if nom_virus == 'Aucun' or not nom_virus:
            messagebox.showwarning("Avertissement", "Aucun virus sélectionné à supprimer.")
            return
        confirm = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le virus '{nom_virus}'?")
        if confirm:
            virus_path = os.path.join(VIRUS_DIR, f"{nom_virus}.json")
            try:
                os.remove(virus_path)
                messagebox.showinfo("Info", f"Virus '{nom_virus}' supprimé avec succès.")
                self.update_virus_dropdown()
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Le fichier du virus '{nom_virus}' n'a pas été trouvé.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression du virus: {e}")
    
    def quitter_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
        self.root.quit()
    
    def update_graphs(self):
        if not self.statistiques:
            return
        jours = range(1, len(self.statistiques) + 1)
        sains = [etat['sain'] for etat in self.statistiques]
        contamines = [etat['contaminé'] for etat in self.statistiques]
        infectes = [etat['infecté'] for etat in self.statistiques]
        retablis = [etat['rétabli'] for etat in self.statistiques]
        morts = [etat['mort'] for etat in self.statistiques]
        
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
    
    def update_virus_dropdown(self):
        menu = self.dropdown_virus['menu']
        menu.delete(0, 'end')
        self.virus_list = list_viruses()
        if self.virus_list:
            for virus in self.virus_list:
                menu.add_command(label=virus, command=lambda value=virus: self.virus_selection.set(value))
            self.virus_selection.set(self.virus_list[0])
        else:
            menu.add_command(label='Aucun', command=lambda: self.virus_selection.set('Aucun'))
            self.virus_selection.set('Aucun')

# Fenêtre de paramètres
class ParameterWindow:
    def __init__(self, parent, simulation_app):
        self.parent = parent
        self.simulation_app = simulation_app
        self.window = tk.Toplevel(parent)
        self.window.title("Modifier les paramètres")
        self.window.geometry("700x800")
        self.setup_parameters()
    
    def setup_parameters(self):
        canvas = tk.Canvas(self.window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        frame = tk.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor='nw')
        
        sections = {
            "Paramètres de la Vie": [
                ("Nombre de sains", self.simulation_app.initial_sains),
                ("Nombre de contaminés", self.simulation_app.initial_contamines),
                ("Nombre d'infectés", self.simulation_app.initial_infectes),
                ("Nombre de rétablis", self.simulation_app.initial_retablis),
                ("Nombre de morts", self.simulation_app.initial_morts)
            ],
            "Paramètres du Virus": [
                ("Probabilité de contamination (%)", self.simulation_app.prob_contamination),
                ("Durée d'incubation (jours)", self.simulation_app.duree_incubation),
                ("Durée d'infection (jours)", self.simulation_app.duree_infection)
            ],
            "Paramètres de la Rétablissement": [
                ("Probabilité de vaccination (%)", self.simulation_app.prob_vaccination),
                ("Durée d'immunité (jours)", self.simulation_app.duree_immunite)
            ],
            "Paramètres de la Mortalité": [
                ("Taux de mortalité (%)", self.simulation_app.taux_mortalite)
            ],
            "Simulation": [
                ("Nombre de jours de simulation", self.simulation_app.nombre_jours),
                ("Discrétisation (jours)", self.simulation_app.discretisation)
            ]
        }
        
        row = 0
        for section, params in sections.items():
            tk.Label(frame, text=section + ":", font=("Helvetica", 12, "bold"))\
                .grid(row=row, column=0, columnspan=2, pady=(10,0), sticky='w')
            row += 1
            for label, var in params:
                tk.Label(frame, text=label).grid(row=row, column=0, padx=10, pady=5, sticky='e')
                entry = tk.Entry(frame, textvariable=var)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                if "%" in label:
                    var.set(var.get() * 100)  # Afficher en pourcentage
                row += 1
        
        # Bouton pour appliquer les changements
        tk.Button(frame, text="Appliquer", command=self.appliquer_changements).grid(row=row, column=0, columnspan=2, pady=20)
    
    def appliquer_changements(self):
        try:
            # Convertir les pourcentages en fractions
            self.simulation_app.prob_contamination.set(self.simulation_app.prob_contamination.get() / 100)
            self.simulation_app.prob_vaccination.set(self.simulation_app.prob_vaccination.get() / 100)
            self.simulation_app.taux_mortalite.set(self.simulation_app.taux_mortalite.get() / 100)
            
            # Validation des paramètres
            total_initial = (
                self.simulation_app.initial_sains.get() +
                self.simulation_app.initial_contamines.get() +
                self.simulation_app.initial_infectes.get() +
                self.simulation_app.initial_retablis.get() +
                self.simulation_app.initial_morts.get()
            )
            if total_initial > 10000:
                messagebox.showerror("Erreur", "La population totale ne doit pas dépasser 10 000 individus.")
                return
            if not (0 <= self.simulation_app.prob_contamination.get() <= 1):
                messagebox.showerror("Erreur", "La probabilité de contamination doit être entre 0 et 1.")
                return
            if not (0 <= self.simulation_app.prob_vaccination.get() <= 1):
                messagebox.showerror("Erreur", "La probabilité de vaccination doit être entre 0 et 1.")
                return
            if not (0 <= self.simulation_app.taux_mortalite.get() <= 1):
                messagebox.showerror("Erreur", "Le taux de mortalité doit être entre 0 et 1.")
                return
            if self.simulation_app.duree_incubation.get() <= 0 or self.simulation_app.duree_infection.get() <= 0 or self.simulation_app.duree_immunite.get() <= 0:
                messagebox.showerror("Erreur", "Les durées doivent être des nombres positifs.")
                return
            if self.simulation_app.nombre_jours.get() <= 0:
                messagebox.showerror("Erreur", "Le nombre de jours de simulation doit être un nombre positif.")
                return
            if self.simulation_app.discretisation.get() <= 0:
                messagebox.showerror("Erreur", "La discrétisation doit être un nombre positif.")
                return
            
            # Mise à jour des labels et fermeture de la fenêtre
            self.simulation_app.mettre_a_jour_label_parametres()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'application des changements: {e}")

# Classe des graphiques
class MainWindow:
    def __init__(self, root, simulation_app):
        self.root = root
        self.simulation_app = simulation_app
        # Les graphiques sont déjà configurés dans setup_gui de SimulationApp
    
    # Pas besoin de méthode supplémentaire ici dans ce fichier unique

# Lancer l'application
if __name__ == "__main__":
    # Création du répertoire 'virus' s'il n'existe pas
    if not os.path.exists(VIRUS_DIR):
        os.makedirs(VIRUS_DIR)
    
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
