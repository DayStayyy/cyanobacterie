import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.users_file = "data/users.json"
        self.lakes_file = "data/lakes.json"
        self._ensure_data_files()

    def _ensure_data_files(self):
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        
        # Créer users.json s'il n'existe pas
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        
        # Créer lakes.json s'il n'existe pas
        if not os.path.exists(self.lakes_file):
            with open(self.lakes_file, 'w') as f:
                json.dump({}, f)

    def load_users(self):
        with open(self.users_file, 'r') as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def load_lakes(self):
        with open(self.lakes_file, 'r') as f:
            return json.load(f)

    def save_lakes(self, lakes):
        with open(self.lakes_file, 'w') as f:
            json.dump(lakes, f, indent=2)

    def register_user(self, username, password):
        users = self.load_users()
        if username in users:
            return False, "Nom d'utilisateur déjà pris"
        
        users[username] = {
            "password": password,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_users(users)
        return True, "Utilisateur créé avec succès"

    def verify_user(self, username, password):
        users = self.load_users()
        if username not in users:
            return False
        return users[username]["password"] == password

    def add_lake(self, username, lake_name, latitude, longitude, lake_type):
        lakes = self.load_lakes()
        if username not in lakes:
            lakes[username] = []
        
        # Vérifier si le lac existe déjà pour cet utilisateur
        for lake in lakes[username]:
            if lake["name"] == lake_name:
                return False, "Un lac avec ce nom existe déjà"
        
        lakes[username].append({
            "name": lake_name,
            "latitude": latitude,
            "longitude": longitude,
            "type": lake_type,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        self.save_lakes(lakes)
        return True, "Lac ajouté avec succès"

    def get_user_lakes(self, username):
        lakes = self.load_lakes()
        return lakes.get(username, [])