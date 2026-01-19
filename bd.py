import os
import psycopg2

# Récupère l'URL de la base depuis l'environnement (plus sûr pour Render)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Connexion à la base
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connexion à la base Render réussie !")
except Exception as e:
    print("Erreur de connexion à la base Render :", e)
