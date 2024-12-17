# gui/parameter_window.py
import tkinter as tk
from tkinter import messagebox, simpledialog

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
            tk.Label(frame, text=section + ":", font=("Helvetica", 12, "bold")).grid(row=row, column=0, columnspan=2, pady=(10,0), sticky='w')
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
