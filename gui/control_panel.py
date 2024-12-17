# gui/control_panel.py
import tkinter as tk
from tkinter import messagebox, simpledialog

class ControlPanel:
    def __init__(self, parent, simulation_app):
        self.parent = parent
        self.simulation_app = simulation_app
        self.setup_controls()
    
    def setup_controls(self):
        # Boutons de contrôle
        tk.Button(self.parent, text="Lancer la simulation", command=self.simulation_app.lancer_simulation)\
            .grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.parent, text="Arrêter la simulation", command=self.simulation_app.arreter_simulation)\
            .grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.parent, text="Réinitialiser", command=self.simulation_app.reinitialiser_simulation)\
            .grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.parent, text="Modifier les paramètres", command=self.simulation_app.ouvrir_fenetre_parametres)\
            .grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        tk.Button(self.parent, text="Quitter", command=self.simulation_app.quitter_simulation)\
            .grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Affichage des paramètres
        tk.Label(self.parent, text="Paramètres actuels:", font=("Helvetica", 10, "bold"))\
            .grid(row=5, column=0, columnspan=2, pady=(10, 0))
        self.label_parametres = tk.Label(self.parent, text="", justify="left")
        self.label_parametres.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky='ew')
        
        # Gestion des virus
        tk.Label(self.parent, text="Gestion des virus:", font=("Helvetica", 10, "bold"))\
            .grid(row=7, column=0, columnspan=2, pady=(10, 0))
        tk.Button(self.parent, text="Sauvegarder comme Virus", command=self.simulation_app.sauvegarder_comme_virus)\
            .grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        tk.Label(self.parent, text="Charger un Virus:").grid(row=9, column=0, padx=5, pady=5, sticky='e')
        self.virus_selection = tk.StringVar()
        self.virus_list = self.simulation_app.utils.list_viruses()  # Accès via self.utils
        options = self.virus_list if self.virus_list else ['Aucun']
        self.virus_selection.set(options[0] if options else 'Aucun')
        self.dropdown_virus = tk.OptionMenu(self.parent, self.virus_selection, *options)
        self.dropdown_virus.grid(row=9, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Button(self.parent, text="Charger Virus", command=self.simulation_app.charger_virus)\
            .grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        tk.Button(self.parent, text="Supprimer Virus", command=self.simulation_app.supprimer_virus)\
            .grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Discrétisation
        tk.Label(self.parent, text="Discrétisation (jours):").grid(row=12, column=0, padx=5, pady=5, sticky='e')
        self.entry_discretisation = tk.Entry(self.parent, textvariable=self.simulation_app.discretisation)
        self.entry_discretisation.grid(row=12, column=1, padx=5, pady=5, sticky='w')
        
        # Espacement flexible
        tk.Label(self.parent).grid(row=15, column=0, columnspan=2, pady=10)
    
    def update_virus_dropdown(self):
        menu = self.dropdown_virus['menu']
        menu.delete(0, 'end')
        self.virus_list = self.simulation_app.utils.list_viruses()  # Accès via self.utils
        if self.virus_list:
            for virus in self.virus_list:
                menu.add_command(label=virus, command=lambda value=virus: self.virus_selection.set(value))
            self.virus_selection.set(self.virus_list[0])
        else:
            menu.add_command(label='Aucun', command=lambda: self.virus_selection.set('Aucun'))
            self.virus_selection.set('Aucun')
