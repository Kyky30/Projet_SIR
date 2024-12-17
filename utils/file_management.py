# utils/file_management.py
import json
import os

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
