import os
import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(page_title="Gestion Examens", layout="wide")
st.title("Emploi du Temps des Examens Universitaires")

# Connexion PostgreSQL Render

# Récupère l'URL de la base depuis les variables d'environnement (Render)
DATABASE_URL = os.environ.get("DATABASE_URL")


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL non trouvé")
    st.stop()
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
# Chargement départements
cur.execute("SELECT id, nom FROM departements ORDER BY nom")
departements = cur.fetchall()
dept_dict = {nom: id for id, nom in departements}
selected_dept = st.selectbox("Département", list(dept_dict.keys()))
dept_id = dept_dict[selected_dept]

# Chargement formations
cur.execute("SELECT id, nom, dept_id FROM formations")
formations = cur.fetchall()
formation_dict = {nom: (fid, did) for fid, nom, did in formations}
formations_dept = [nom for nom, (fid, did) in formation_dict.items() if did == dept_id]
selected_formation = st.selectbox("Formation", formations_dept)
formation_id = formation_dict[selected_formation][0]


# Chargement professeurs
cur.execute("SELECT id, nom FROM professeurs")
professeurs = cur.fetchall()
prof_dict = {nom: id for id, nom in professeurs}
selected_prof = st.selectbox("Professeur", ["Tous"] + list(prof_dict.keys()))
prof_id = None if selected_prof == "Tous" else prof_dict[selected_prof]


# Requête planning
query = f"""
SELECT 
    e.id AS examen_id,
    m.nom AS module,
    f.nom AS formation,
    d.nom AS departement,
    p.nom AS professeur,
    l.nom AS salle,
    l.capacite,
    e.date_heure,
    e.duree_minutes
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
JOIN professeurs p ON e.prof_id = p.id
JOIN lieu_examen l ON e.salle_id = l.id
WHERE f.id = {formation_id}
"""
if prof_id:
    query += f" AND p.id = {prof_id}"
query += " ORDER BY e.date_heure"

df = pd.read_sql(query, conn)
df['date_heure'] = pd.to_datetime(df['date_heure'])


# Affichage
st.dataframe(df, use_container_width=True)

# Génération automatique
if st.button("Générer automatiquement le planning"):
    cur.execute("CALL generer_planning()")
    conn.commit()
    st.success("Planning généré !")

cur.close()
conn.close()
