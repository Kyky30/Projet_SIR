# simulation.py
import random

class Individu:
    def __init__(self):
        self.etat = 'sain'  # 'sain', 'contaminé', 'infecté', 'rétabli', 'mort'
        self.jours_incubation = 0  # Nombre de jours restants avant devenir infecté
        self.jours_infection = 0    # Nombre de jours restants avant rétablissement ou décès
        self.jours_immunite = 0     # Nombre de jours restants d'immunité

    def contaminer(self, prob_contamination):
        if self.etat == 'sain' and random.random() < prob_contamination:
            self.etat = 'contaminé'
            return True
        return False

    def devenir_infecte(self, duree_incubation):
        if self.etat == 'contaminé':
            self.jours_incubation += 1
            if self.jours_incubation >= duree_incubation:
                self.etat = 'infecté'
                self.jours_infection = 0

    def vacciner(self, duree_immunite):
        if self.etat == 'sain':
            self.etat = 'rétabli'
            self.jours_immunite = duree_immunite

    def jour_suivant(self, duree_infection, duree_immunite, duree_incubation, taux_mortalite):
        if self.etat == 'contaminé':
            self.devenir_infecte(duree_incubation)
        elif self.etat == 'infecté':
            self.jours_infection += 1
            if self.jours_infection >= duree_infection:
                if random.random() < taux_mortalite:
                    self.etat = 'mort'
                else:
                    self.etat = 'rétabli'
                    self.jours_immunite = duree_immunite
        elif self.etat == 'rétabli':
            self.jours_immunite -= 1
            if self.jours_immunite <= 0:
                self.etat = 'sain'

class Population:
    def __init__(self, initial_sains, initial_contamines, initial_infectes, initial_retablis, initial_morts):
        self.individus = []
        # Ajouter les individus sains
        for _ in range(initial_sains):
            self.individus.append(Individu())
        # Ajouter les individus contaminés
        for _ in range(initial_contamines):
            individu = Individu()
            individu.etat = 'contaminé'
            self.individus.append(individu)
        # Ajouter les individus infectés
        for _ in range(initial_infectes):
            individu = Individu()
            individu.etat = 'infecté'
            self.individus.append(individu)
        # Ajouter les individus rétablis
        for _ in range(initial_retablis):
            individu = Individu()
            individu.etat = 'rétabli'
            self.individus.append(individu)
        # Ajouter les individus morts
        for _ in range(initial_morts):
            individu = Individu()
            individu.etat = 'mort'
            self.individus.append(individu)

    def compter_etats(self):
        etats = {'sains': 0, 'contamines': 0, 'infectes': 0, 'retablis': 0, 'morts': 0}
        for individu in self.individus:
            if individu.etat in etats:
                etats[individu.etat] += 1
        return etats

    def propager_infection(self, prob_contamination):
        # Compter le nombre d'infectés
        nb_infectes = sum(1 for individu in self.individus if individu.etat == 'infecté')
        if nb_infectes == 0:
            return  # Pas de propagation si personne n'est infecté
        for individu in self.individus:
            if individu.etat == 'sain':
                # La probabilité de contamination est influencée par le nombre d'infectés
                prob = prob_contamination * (nb_infectes / len(self.individus))
                individu.contaminer(prob)

    def vacciner_population(self, prob_vaccination, duree_immunite):
        for individu in self.individus:
            if individu.etat == 'sain' and random.random() < prob_vaccination:
                individu.vacciner(duree_immunite)

    def jour_suivant(self, duree_infection, duree_immunite, duree_incubation, taux_mortalite):
        for individu in self.individus:
            individu.jour_suivant(duree_infection, duree_immunite, duree_incubation, taux_mortalite)

def simuler(population, prob_contamination, duree_incubation, duree_infection, prob_vaccination, duree_immunite, taux_mortalite, nombre_jours, callback=None):
    statistiques = []
    for jour in range(nombre_jours):
        # Propagation de l'infection
        population.propager_infection(prob_contamination)
        # Vaccination de la population
        population.vacciner_population(prob_vaccination, duree_immunite)
        # Passage au jour suivant (gestion de l'incubation, infection, rétablissement et mortalité)
        population.jour_suivant(duree_infection, duree_immunite, duree_incubation, taux_mortalite)
        # Comptage des états
        etats = population.compter_etats()
        statistiques.append(etats)
        print(f"Jour {jour+1}: {etats}")
        if callback:
            callback(jour+1, etats, statistiques)
    return statistiques
