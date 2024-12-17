# simulation/differential_equations.py
import numpy as np
from scipy.integrate import odeint

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
