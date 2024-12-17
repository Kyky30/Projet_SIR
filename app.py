# app.py
import tkinter as tk
from gui.main_window import MainWindow
from gui.control_panel import ControlPanel
from gui.parameter_window import ParameterWindow
from simulation import simulate_seir
import utils.file_management as utils_module  # Import complet du module
from tkinter import messagebox, simpledialog
from matplotlib import pyplot as plt
import os

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
        self.utils = utils_module
        
        # Initialisation des composants GUI
        self.control_panel = ControlPanel(root, self)
        self.main_window = MainWindow(root, self)
        
        # Mettre à jour les paramètres affichés après initialisation complète
        self.mettre_a_jour_label_parametres()
    
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
        self.control_panel.label_parametres.config(text=texte)
    
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
            self.main_window.update_graphs(self.statistiques)
            
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
        self.main_window.clear_graphs()
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
            self.control_panel.update_virus_dropdown()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde du virus: {e}")
    
    def charger_virus(self):
        nom_virus = self.control_panel.virus_selection.get()
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
            self.main_window.update_graphs(self.statistiques)
            messagebox.showinfo("Info", f"Virus '{nom_virus}' chargé avec succès.")
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Le virus '{nom_virus}' n'a pas été trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du virus: {e}")
    
    def supprimer_virus(self):
        nom_virus = self.control_panel.virus_selection.get()
        if nom_virus == 'Aucun' or not nom_virus:
            messagebox.showwarning("Avertissement", "Aucun virus sélectionné à supprimer.")
            return
        confirm = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le virus '{nom_virus}'?")
        if confirm:
            virus_path = os.path.join('virus', f"{nom_virus}.json")
            try:
                os.remove(virus_path)
                messagebox.showinfo("Info", f"Virus '{nom_virus}' supprimé avec succès.")
                self.control_panel.update_virus_dropdown()
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Le fichier du virus '{nom_virus}' n'a pas été trouvé.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression du virus: {e}")
    
    def quitter_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
        self.root.quit()

if __name__ == "__main__":
    # Création du répertoire 'virus' s'il n'existe pas
    if not os.path.exists('virus'):
        os.makedirs('virus')
    
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
