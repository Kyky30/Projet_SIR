# app.py
import tkinter as tk
from tkinter import messagebox, Toplevel, simpledialog
from simulation import Population  # Assure-toi que simulation.py contient la classe Population
from utils import (
    afficher_statistiques,
    save_virus,
    load_virus,
    list_viruses
)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Nécessaire pour les graphiques 3D
import os

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation de propagation")
        self.root.geometry("1600x900")  # Taille ajustée pour mieux accueillir les graphiques
        self.root.minsize(1200, 700)    # Taille minimale pour éviter les écrans trop petits

        # Configurer le grid de la fenêtre principale avec des poids de colonne
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=0)  # Control frame
        self.root.columnconfigure(1, weight=1)  # Graph frame

        # Paramètres organisés en catégories
        # Paramètres de la Vie
        self.initial_sains = tk.IntVar(value=990)
        self.initial_contamines = tk.IntVar(value=0)
        self.initial_infectes = tk.IntVar(value=10)
        self.initial_retablis = tk.IntVar(value=0)
        self.initial_morts = tk.IntVar(value=0)

        # Paramètres du Virus
        self.prob_contamination = tk.DoubleVar(value=0.15)  # Fraction (15%)
        self.duree_incubation = tk.IntVar(value=3)          # 3 jours d'incubation
        self.duree_infection = tk.IntVar(value=7)           # 7 jours pour se rétablir

        # Paramètres de la Rétablissement
        self.prob_vaccination = tk.DoubleVar(value=0.05)    # Fraction (5%)
        self.duree_immunite = tk.IntVar(value=30)           # 30 jours d'immunité

        # Paramètres de la Mortalité
        self.taux_mortalite = tk.DoubleVar(value=0.02)      # Taux de mortalité (2%)

        # Nombre de jours de simulation
        self.nombre_jours = tk.IntVar(value=100)            # 100 jours de simulation

        # Nombre de jours par discrétisation
        self.discretisation = tk.IntVar(value=10)           # 10 jours par itération

        # Interface graphique
        self.create_widgets()
        self.population = None
        self.simulation_running = False
        self.current_jour = 0
        self.statistiques = []

        # Création de la frame pour les graphiques
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self.graph_frame.rowconfigure(0, weight=1)
        self.graph_frame.columnconfigure(0, weight=1)

        # Création de la figure matplotlib avec trois sous-graphiques
        self.fig = plt.Figure(figsize=(16, 9), tight_layout=True)
        
        # Graphique linéaire 2D
        self.ax_linear = self.fig.add_subplot(221)
        self.ax_linear.set_title("Évolution de la population")
        self.ax_linear.set_xlabel("Jour")
        self.ax_linear.set_ylabel("Nombre d'individus")

        # Diagramme de phase 3D
        self.ax_3d = self.fig.add_subplot(222, projection='3d')
        self.ax_3d.set_title("Diagramme de phase en 3D")
        self.ax_3d.set_xlabel("Sains")
        self.ax_3d.set_ylabel("Infectés")
        self.ax_3d.set_zlabel("Rétablis")

        # Graphique combiné S, I, R, D
        self.ax_combined = self.fig.add_subplot(223)
        self.ax_combined.set_title("S, I, R, D - Évolution")
        self.ax_combined.set_xlabel("Jour")
        self.ax_combined.set_ylabel("Nombre d'individus")

        # Création des sous-frames pour le canvas et la toolbar
        self.graph_canvas_frame = tk.Frame(self.graph_frame)
        self.graph_canvas_frame.grid(row=0, column=0, sticky='nsew')
        self.graph_canvas_frame.rowconfigure(0, weight=1)
        self.graph_canvas_frame.columnconfigure(0, weight=1)

        self.graph_toolbar_frame = tk.Frame(self.graph_frame)
        self.graph_toolbar_frame.grid(row=1, column=0, sticky='ew')

        # Création du canvas et ajout à la frame graphique
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Ajouter la barre de navigation de Matplotlib dans graph_toolbar_frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_toolbar_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_widgets(self):
        # Création de la frame pour les contrôles
        self.control_frame = tk.Frame(self.root, padx=10, pady=10)
        self.control_frame.grid(row=0, column=0, sticky='nsew')

        # Configurer le grid de la frame de contrôle
        self.control_frame.rowconfigure(15, weight=1)  # Espacement flexible
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)

        # Boutons pour interagir avec la simulation
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

        # Labels pour afficher les paramètres actuels
        tk.Label(self.control_frame, text="Paramètres actuels:", font=("Helvetica", 10, "bold"))\
            .grid(row=5, column=0, columnspan=2, pady=(10, 0))
        self.label_parametres = tk.Label(self.control_frame, text="", justify="left")
        self.label_parametres.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky='ew')
        self.mettre_a_jour_label_parametres()

        # Ajouter la section pour gérer les virus
        tk.Label(self.control_frame, text="Gestion des virus:", font=("Helvetica", 10, "bold"))\
            .grid(row=7, column=0, columnspan=2, pady=(10, 0))

        # Bouton pour sauvegarder les paramètres actuels comme virus
        tk.Button(self.control_frame, text="Sauvegarder comme Virus", command=self.sauvegarder_comme_virus)\
            .grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Dropdown pour sélectionner un virus à charger
        tk.Label(self.control_frame, text="Charger un Virus:").grid(row=9, column=0, padx=5, pady=5, sticky='e')
        self.virus_selection = tk.StringVar()
        self.virus_list = list_viruses()
        if self.virus_list:
            self.virus_selection.set(self.virus_list[0])
        else:
            self.virus_selection.set('Aucun')  # Option par défaut si aucun virus n'est présent
        options = self.virus_list if self.virus_list else ['Aucun']
        self.dropdown_virus = tk.OptionMenu(self.control_frame, self.virus_selection, *options)
        self.dropdown_virus.grid(row=9, column=1, padx=5, pady=5, sticky='ew')

        # Bouton pour charger le virus sélectionné
        tk.Button(self.control_frame, text="Charger Virus", command=self.charger_virus)\
            .grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Bouton pour supprimer un virus
        tk.Button(self.control_frame, text="Supprimer Virus", command=self.supprimer_virus)\
            .grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Nouveau paramètre: Discrétisation
        tk.Label(self.control_frame, text="Discrétisation (jours):").grid(row=12, column=0, padx=5, pady=5, sticky='e')
        self.entry_discretisation = tk.Entry(self.control_frame, textvariable=self.discretisation)
        self.entry_discretisation.grid(row=12, column=1, padx=5, pady=5, sticky='w')

        # Spacer pour pousser les éléments vers le haut
        tk.Label(self.control_frame).grid(row=15, column=0, columnspan=2, pady=10)

    def mettre_a_jour_label_parametres(self):
        texte = (
            f"--- Paramètres de la Vie ---\n"
            f"Nombre de sains: {self.initial_sains.get()}\n"
            f"Nombre de contaminés: {self.initial_contamines.get()}\n"
            f"Nombre d'infectés: {self.initial_infectes.get()}\n"
            f"Nombre de rétablis: {self.initial_retablis.get()}\n"
            f"Nombre de morts: {self.initial_morts.get()}\n\n"
            f"--- Paramètres du Virus ---\n"
            f"Probabilité de contamination: {self.prob_contamination.get() * 100}%\n"
            f"Durée d'incubation: {self.duree_incubation.get()} jours\n"
            f"Durée d'infection: {self.duree_infection.get()} jours\n\n"
            f"--- Paramètres de la Rétablissement ---\n"
            f"Probabilité de vaccination: {self.prob_vaccination.get() * 100}%\n"
            f"Durée d'immunité: {self.duree_immunite.get()} jours\n\n"
            f"--- Paramètres de la Mortalité ---\n"
            f"Taux de mortalité: {self.taux_mortalite.get() * 100}%\n\n"
            f"Nombre de jours de simulation: {self.nombre_jours.get()}\n"
            f"Discrétisation (jours): {self.discretisation.get()}"
        )
        self.label_parametres.config(text=texte)

    def ouvrir_fenetre_parametres(self):
        param_window = Toplevel(self.root)
        param_window.title("Modifier les paramètres")
        param_window.geometry("700x800")  # Ajusté pour inclure la discrétisation

        # Configurer le grid de la fenêtre de paramètres
        param_window.rowconfigure(0, weight=1)
        param_window.columnconfigure(0, weight=1)

        # Canvas pour permettre le scroll si nécessaire
        canvas = tk.Canvas(param_window)
        canvas.grid(row=0, column=0, sticky='nsew')

        scrollbar = tk.Scrollbar(param_window, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor='nw')

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Labels et champs de saisie pour les paramètres organisés en sections
        sections = {
            "Paramètres de la Vie": [
                ("Nombre de sains", self.initial_sains),
                ("Nombre de contaminés", self.initial_contamines),
                ("Nombre d'infectés", self.initial_infectes),
                ("Nombre de rétablis", self.initial_retablis),
                ("Nombre de morts", self.initial_morts)
            ],
            "Paramètres du Virus": [
                ("Probabilité de contamination (%)", self.prob_contamination),
                ("Durée d'incubation (jours)", self.duree_incubation),
                ("Durée d'infection (jours)", self.duree_infection)
            ],
            "Paramètres de la Rétablissement": [
                ("Probabilité de vaccination (%)", self.prob_vaccination),
                ("Durée d'immunité (jours)", self.duree_immunite)
            ],
            "Paramètres de la Mortalité": [
                ("Taux de mortalité (%)", self.taux_mortalite)
            ],
            "Simulation": [
                ("Nombre de jours de simulation", self.nombre_jours),
                ("Discrétisation (jours)", self.discretisation)  # Nouvelle entrée
            ]
        }

        row_offset = 0
        for section, params in sections.items():
            tk.Label(frame, text=section + ":", font=("Helvetica", 12, "bold"))\
                .grid(row=row_offset, column=0, columnspan=2, pady=(10, 0), sticky='w')
            row_offset += 1
            for label, var in params:
                tk.Label(frame, text=label).grid(row=row_offset, column=0, padx=10, pady=5, sticky='e')
                entry = tk.Entry(frame, textvariable=var)
                entry.grid(row=row_offset, column=1, padx=10, pady=5, sticky='w')
                if "%" in label:
                    var.set(var.get() * 100)  # Afficher en pourcentage
                row_offset += 1

        # Bouton pour appliquer les changements
        def appliquer_changements():
            try:
                # Convertir les probabilités de pourcentage à fraction
                self.prob_contamination.set(self.prob_contamination.get() / 100)
                self.prob_vaccination.set(self.prob_vaccination.get() / 100)
                self.taux_mortalite.set(self.taux_mortalite.get() / 100)

                # Valider que les nombres sont cohérents
                total_initial = (
                    self.initial_sains.get() +
                    self.initial_contamines.get() +
                    self.initial_infectes.get() +
                    self.initial_retablis.get() +
                    self.initial_morts.get()
                )
                if total_initial > 10000:
                    messagebox.showerror("Erreur", "La population totale ne doit pas dépasser 10 000 individus.")
                    return
                if not (0 <= self.prob_contamination.get() <= 1):
                    messagebox.showerror("Erreur", "La probabilité de contamination doit être entre 0 et 1.")
                    return
                if not (0 <= self.prob_vaccination.get() <= 1):
                    messagebox.showerror("Erreur", "La probabilité de vaccination doit être entre 0 et 1.")
                    return
                if not (0 <= self.taux_mortalite.get() <= 1):
                    messagebox.showerror("Erreur", "Le taux de mortalité doit être entre 0 et 1.")
                    return
                if self.duree_incubation.get() <= 0 or self.duree_infection.get() <= 0 or self.duree_immunite.get() <= 0:
                    messagebox.showerror("Erreur", "Les durées doivent être des nombres positifs.")
                    return
                if self.nombre_jours.get() <= 0:
                    messagebox.showerror("Erreur", "Le nombre de jours de simulation doit être un nombre positif.")
                    return
                if self.discretisation.get() <= 0:
                    messagebox.showerror("Erreur", "La discrétisation doit être un nombre positif.")
                    return

                self.mettre_a_jour_label_parametres()
                param_window.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'application des changements: {e}")

        tk.Button(frame, text="Appliquer", command=appliquer_changements)\
            .grid(row=row_offset, column=0, columnspan=2, pady=20)

    def lancer_simulation(self):
        if not self.simulation_running:
            taille_sains = self.initial_sains.get()
            taille_contamines = self.initial_contamines.get()
            taille_infectes = self.initial_infectes.get()
            taille_retablis = self.initial_retablis.get()
            taille_morts = self.initial_morts.get()
            prob_contamination = self.prob_contamination.get()
            duree_incubation = self.duree_incubation.get()
            duree_infection = self.duree_infection.get()
            prob_vaccination = self.prob_vaccination.get()
            duree_immunite = self.duree_immunite.get()
            taux_mortalite = self.taux_mortalite.get()
            nombre_jours = self.nombre_jours.get()
            discretisation = self.discretisation.get()

            # Validation des paramètres
            total_population = taille_sains + taille_contamines + taille_infectes + taille_retablis + taille_morts
            if taille_contamines > total_population:
                messagebox.showerror("Erreur", "Le nombre initial de contaminés dépasse la population totale.")
                return
            if taille_infectes > total_population:
                messagebox.showerror("Erreur", "Le nombre initial d'infectés dépasse la population totale.")
                return
            if taille_retablis > total_population:
                messagebox.showerror("Erreur", "Le nombre initial de rétablis dépasse la population totale.")
                return
            if taille_morts > total_population:
                messagebox.showerror("Erreur", "Le nombre initial de morts dépasse la population totale.")
                return
            if total_population > 10000:
                messagebox.showerror("Erreur", "La population totale ne doit pas dépasser 10 000 individus.")
                return
            if not (0 <= prob_contamination <= 1):
                messagebox.showerror("Erreur", "La probabilité de contamination doit être entre 0 et 1.")
                return
            if not (0 <= prob_vaccination <= 1):
                messagebox.showerror("Erreur", "La probabilité de vaccination doit être entre 0 et 1.")
                return
            if not (0 <= taux_mortalite <= 1):
                messagebox.showerror("Erreur", "Le taux de mortalité doit être entre 0 et 1.")
                return
            if duree_incubation <= 0 or duree_infection <= 0 or duree_immunite <= 0:
                messagebox.showerror("Erreur", "Les durées doivent être des nombres positifs.")
                return
            if nombre_jours <= 0:
                messagebox.showerror("Erreur", "Le nombre de jours de simulation doit être un nombre positif.")
                return
            if discretisation <= 0:
                messagebox.showerror("Erreur", "La discrétisation doit être un nombre positif.")
                return

            self.population = Population(
                initial_sains=taille_sains,
                initial_contamines=taille_contamines,
                initial_infectes=taille_infectes,
                initial_retablis=taille_retablis,
                initial_morts=taille_morts
            )
            self.simulation_running = True
            self.current_jour = 0
            self.statistiques = []
            self.simuler_jour()
        else:
            messagebox.showinfo("Info", "Simulation déjà en cours")

    def simuler_jour(self):
        discretisation = self.discretisation.get()  # Nombre de jours par itération
        if self.simulation_running and self.current_jour < self.nombre_jours.get():
            jours_a_simuler = min(discretisation, self.nombre_jours.get() - self.current_jour)
            for _ in range(jours_a_simuler):
                self.current_jour += 1
                self.population.propager_infection(self.prob_contamination.get())
                self.population.vacciner_population(self.prob_vaccination.get(), self.duree_immunite.get())
                self.population.jour_suivant(
                    duree_infection=self.duree_infection.get(),
                    duree_immunite=self.duree_immunite.get(),
                    duree_incubation=self.duree_incubation.get(),
                    taux_mortalite=self.taux_mortalite.get()
                )
                etats = self.population.compter_etats()
                self.statistiques.append(etats)
                print(f"Jour {self.current_jour}: {etats}")

            # Mettre à jour le graphique linéaire 2D et le combiné
            afficher_statistiques(self.statistiques, self.current_jour, self.ax_linear, ax_combined=self.ax_combined)

            # Mettre à jour le diagramme de phase 3D avec projections
            self.plot_3d_phase()

            self.canvas.draw()

            # Planifier le prochain bloc de jours après un court délai (par exemple, 100 ms)
            self.root.after(100, self.simuler_jour)
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
        self.population = None
        self.current_jour = 0
        self.statistiques = []
        # Réinitialiser le graphique linéaire 2D
        self.ax_linear.clear()
        self.ax_linear.set_title("Évolution de la population")
        self.ax_linear.set_xlabel("Jour")
        self.ax_linear.set_ylabel("Nombre d'individus")
        # Réinitialiser le graphique combiné
        self.ax_combined.clear()
        self.ax_combined.set_title("S, I, R, D - Évolution")
        self.ax_combined.set_xlabel("Jour")
        self.ax_combined.set_ylabel("Nombre d'individus")
        # Réinitialiser le diagramme de phase 3D
        self.ax_3d.clear()
        self.ax_3d.set_title("Diagramme de phase en 3D")
        self.ax_3d.set_xlabel("Sains")
        self.ax_3d.set_ylabel("Infectés")
        self.ax_3d.set_zlabel("Rétablis")
        self.canvas.draw()
        self.mettre_a_jour_label_parametres()
        messagebox.showinfo("Info", "Simulation réinitialisée")

    def sauvegarder_comme_virus(self):
        # Demander un nom pour le virus
        nom_virus = simpledialog.askstring("Nom du Virus", "Entrez le nom du virus:")
        if not nom_virus:
            messagebox.showwarning("Avertissement", "Le nom du virus ne peut pas être vide.")
            return

        # Vérifier si un virus avec le même nom existe déjà
        if nom_virus in list_viruses():
            overwrite = messagebox.askyesno("Confirmation", f"Le virus '{nom_virus}' existe déjà. Voulez-vous le remplacer?")
            if not overwrite:
                return

        # Préparer les paramètres à sauvegarder
        parameters = {
            'initial_sains': self.initial_sains.get(),
            'initial_contamines': self.initial_contamines.get(),
            'initial_infectes': self.initial_infectes.get(),
            'initial_retablis': self.initial_retablis.get(),
            'initial_morts': self.initial_morts.get(),
            'prob_contamination': self.prob_contamination.get(),  # Stocker en fraction
            'duree_incubation': self.duree_incubation.get(),
            'duree_infection': self.duree_infection.get(),
            'prob_vaccination': self.prob_vaccination.get(),      # Stocker en fraction
            'duree_immunite': self.duree_immunite.get(),
            'taux_mortalite': self.taux_mortalite.get(),          # Stocker en fraction
            'nombre_jours': self.nombre_jours.get(),
            'discretisation': self.discretisation.get()          # Inclure la discrétisation
        }

        try:
            # Sauvegarder le virus
            save_virus(nom_virus, parameters)
            messagebox.showinfo("Info", f"Virus '{nom_virus}' sauvegardé avec succès.")
            # Mettre à jour la liste des virus
            self.update_virus_list()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde du virus: {e}")

    def update_virus_list(self):
        self.virus_list = list_viruses()
        menu = self.dropdown_virus['menu']
        menu.delete(0, 'end')
        if self.virus_list:
            for virus in self.virus_list:
                menu.add_command(label=virus, command=lambda value=virus: self.virus_selection.set(value))
            self.virus_selection.set(self.virus_list[0])
        else:
            menu.add_command(label='Aucun', command=lambda: self.virus_selection.set('Aucun'))
            self.virus_selection.set('Aucun')

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
            self.prob_contamination.set(parameters['prob_contamination'])  # Stocker en fraction
            self.duree_incubation.set(parameters['duree_incubation'])
            self.duree_infection.set(parameters['duree_infection'])
            self.prob_vaccination.set(parameters['prob_vaccination'])      # Stocker en fraction
            self.duree_immunite.set(parameters['duree_immunite'])
            self.taux_mortalite.set(parameters['taux_mortalite'])          # Stocker en fraction
            self.nombre_jours.set(parameters['nombre_jours'])
            self.discretisation.set(parameters.get('discretisation', 10))  # Valeur par défaut si absent
            # Mettre à jour les labels
            self.mettre_a_jour_label_parametres()
            # Mettre à jour les graphiques avec les nouveaux paramètres
            afficher_statistiques(self.statistiques, self.current_jour, self.ax_linear, ax_combined=self.ax_combined)
            self.plot_3d_phase()
            self.canvas.draw()
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
            virus_path = os.path.join('virus', f"{nom_virus}.json")
            try:
                os.remove(virus_path)
                messagebox.showinfo("Info", f"Virus '{nom_virus}' supprimé avec succès.")
                self.update_virus_list()
                # Réinitialiser la sélection si le virus supprimé était sélectionné
                if not self.virus_list:
                    self.virus_selection.set('Aucun')
                else:
                    self.virus_selection.set(self.virus_list[0])
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Le fichier du virus '{nom_virus}' n'a pas été trouvé.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression du virus: {e}")

    def quitter_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
        self.root.quit()

    def plot_3d_phase(self):
        # Extraire les données
        sains = [etat['sains'] for etat in self.statistiques]
        contamines = [etat['contamines'] for etat in self.statistiques]
        infectes = [etat['infectes'] for etat in self.statistiques]
        retablis = [etat['retablis'] for etat in self.statistiques]
        morts = [etat['morts'] for etat in self.statistiques]

        # Tracer la courbe en 3D sans légende
        self.ax_3d.clear()
        self.ax_3d.set_title("Diagramme de phase en 3D")
        self.ax_3d.set_xlabel("Sains")
        self.ax_3d.set_ylabel("Infectés")
        self.ax_3d.set_zlabel("Rétablis")

        # Tracer la ligne principale
        self.ax_3d.plot(sains, infectes, retablis, color='purple', label='Trajectoire')

        # Ajouter une petite boule au début du tracé avec taille augmentée
        if sains and infectes and retablis:
            self.ax_3d.scatter(sains[0], infectes[0], retablis[0],
                              color='green', s=100, label='Début')  # Taille = 100

        # Ajouter une petite boule à la fin du tracé avec taille augmentée
        if sains and infectes and retablis:
            self.ax_3d.scatter(sains[-1], infectes[-1], retablis[-1],
                              color='red', s=100, label='Fin')  # Taille = 100

        # Ajouter des projections sur les différents plans

        # Projection sur le plan Sains-Infectés (z = 0)
        self.ax_3d.plot(sains, infectes, [0]*len(sains), color='blue', linestyle='--', label='Projection S-I')

        # Projection sur le plan Sains-Rétablis (y = 0)
        self.ax_3d.plot(sains, [0]*len(sains), retablis, color='orange', linestyle='--', label='Projection S-R')

        # Projection sur le plan Infectés-Rétablis (x = 0)
        self.ax_3d.plot([0]*len(infectes), infectes, retablis, color='cyan', linestyle='--', label='Projection I-R')

        # Projection sur le plan Contaminés-Infectés (C-I)
        self.ax_3d.plot(contamines, infectes, [0]*len(contamines), color='magenta', linestyle=':', label='Projection C-I')

        # Projection sur le plan Contaminés-Rétablis (C-R)
        self.ax_3d.plot(contamines, [0]*len(contamines), retablis, color='brown', linestyle=':', label='Projection C-R')

        # Projection sur le plan Contaminés-Morts (C-D)
        self.ax_3d.plot([0]*len(contamines), contamines, morts, color='grey', linestyle=':', label='Projection C-D')

        # Projection sur le plan Infectés-Morts (I-D)
        self.ax_3d.plot(infectes, [0]*len(infectes), morts, color='black', linestyle=':', label='Projection I-D')

        # Projection sur le plan Rétablis-Morts (R-D)
        self.ax_3d.plot([0]*len(retablis), retablis, morts, color='purple', linestyle=':', label='Projection R-D')

        # Ajouter une légende
        self.ax_3d.legend(loc='upper left')

        # Améliorer l'esthétique du graphique
        self.ax_3d.view_init(elev=20., azim=30)  # Ajuster l'angle de vue si nécessaire

        # Ajuster les limites des axes pour mieux visualiser les projections
        max_sains = max(sains) if sains else 1
        max_infectes = max(infectes) if infectes else 1
        max_retablis = max(retablis) if retablis else 1
        max_contamines = max(contamines) if contamines else 1
        max_morts = max(morts) if morts else 1
        self.ax_3d.set_xlim(0, max_sains * 1.1)
        self.ax_3d.set_ylim(0, max_infectes * 1.1)
        self.ax_3d.set_zlim(0, max_retablis * 1.1)

    def plot_linear_graph(self):
        # Cette méthode est déjà gérée par afficher_statistiques
        pass

if __name__ == "__main__":
    # Créer le répertoire 'virus' s'il n'existe pas
    if not os.path.exists('virus'):
        os.makedirs('virus')

    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
