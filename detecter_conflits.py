import psycopg2
import pandas as pd
import time  # <-- Ajouté pour mesurer le temps

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="gestion_examens",
    user="postgres",
    password="1234"
)

# Requêtes de détection de conflits
queries = {
    "Conflits étudiants": """
        SELECT i.etudiant_id, DATE(e.date_heure) AS jour, COUNT(*) 
        FROM inscriptions i
        JOIN examens e ON i.module_id = e.module_id
        GROUP BY i.etudiant_id, DATE(e.date_heure)
        HAVING COUNT(*) > 1;
    """,

    "Conflits professeurs": """
        SELECT prof_id, DATE(date_heure), COUNT(*)
        FROM examens
        GROUP BY prof_id, DATE(date_heure)
        HAVING COUNT(*) > 3;
    """,

    "Conflits salles capacité": """
        SELECT e.id, l.nom, l.capacite, COUNT(i.etudiant_id)
        FROM examens e
        JOIN lieu_examen l ON e.salle_id = l.id
        JOIN inscriptions i ON e.module_id = i.module_id
        GROUP BY e.id, l.nom, l.capacite
        HAVING COUNT(i.etudiant_id) > l.capacite;
    """
}

# Exécution et chronométrage
for titre, query in queries.items():
    start = time.time()  # Début chrono
    df = pd.read_sql(query, conn)
    end = time.time()    # Fin chrono
    
    print(f"\n {titre} (Temps d'exécution : {round(end - start, 2)} secondes)")
    if df.empty:
        print(" Aucun conflit")
    else:
        print(df)

# Fermeture de la connexion
conn.close()
