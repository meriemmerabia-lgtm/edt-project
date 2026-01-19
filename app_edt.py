import os
import streamlit as st
import pandas as pd
import psycopg2


# Initialiser le planning dans session_state
if 'planning' not in st.session_state:
    st.session_state.planning = None
# CONFIGURATION STREAMLIT
st.set_page_config(
    page_title="Gestion Examens",
    layout="wide"
)

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

st.title(" Emploi du Temps des Examens Universitaires")

# CONNEXION POSTGRESQL
conn = psycopg2.connect(
    host="aws-1-eu-central-2.pooler.supabase.com",
    port=6543,
    database="postgres",
    user="postgres.ryzlenworqjmdgkanfcj",
    password=os.environ.get("DB_PASSWORD")

)
cur = conn.cursor()

# CHARGEMENT DES DONNÉES
# Départements
cur.execute("SELECT id, nom FROM departements ORDER BY nom")
departements = cur.fetchall()
if not departements:
    st.error("⚠️ Aucun département trouvé")
    st.stop()
dept_dict = {nom: id for id, nom in departements}

# Formations
cur.execute("SELECT id, nom, dept_id FROM formations")
formations = cur.fetchall()
formation_dict = {nom: (fid, did) for fid, nom, did in formations}

# Professeurs
cur.execute("SELECT id, nom FROM professeurs")
professeurs = cur.fetchall()
prof_dict = {nom: id for id, nom in professeurs}

# SÉLECTEURS
selected_dept = st.selectbox(" Département", list(dept_dict.keys()))
dept_id = dept_dict[selected_dept]

formations_dept = [
    nom for nom, (fid, did) in formation_dict.items() if did == dept_id
]

if not formations_dept:
    st.warning("Aucune formation pour ce département")
    st.stop()

selected_formation = st.selectbox(" Formation", formations_dept)
formation_id = formation_dict[selected_formation][0]

selected_prof = st.selectbox(
    " Professeur",
    ["Tous"] + list(prof_dict.keys())
)
prof_id = None if selected_prof == "Tous" else prof_dict[selected_prof]

# REQUÊTE SQL
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

# AFFICHAGE PLANNING
st.subheader(" Planning des Examens")

def color_dept(row):
    colors = {
        "Informatique": "background-color:#f9d5e5",
        "Mathématiques": "background-color:#d5f9e3",
        "Physique": "background-color:#f9f1d5"
    }
    return [colors.get(row.departement, "")] * len(row)

# Filtre par date
dates = sorted(df['date_heure'].dt.date.unique())
selected_date = st.selectbox(" Filtrer par date", dates)

df_filtre = df[df['date_heure'].dt.date == selected_date]

st.dataframe(
    df_filtre.style.apply(color_dept, axis=1),
    use_container_width=True
)
# STATISTIQUES
st.subheader(" Statistiques")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total examens", len(df))
with col2:
    st.metric("Examens ce jour", len(df_filtre))

st.bar_chart(df.groupby("departement").size())

# EXPORT CSV
csv = df_filtre.to_csv(index=False).encode("utf-8")
st.download_button(
    " Télécharger le planning (CSV)",
    data=csv,
    file_name="planning_examens.csv",
    mime="text/csv"
)

# GÉNÉRATION AUTOMATIQUE
if st.button(" Générer automatiquement le planning"):
    try:
        # Appeler ta procédure ou fonction pour générer le planning
        cur.execute("CALL generer_planning()")  # si tu utilises SQL pour générer
        conn.commit()

        # Recharger le planning depuis la base
        df = pd.read_sql(query, conn)
        df['date_heure'] = pd.to_datetime(df['date_heure'])
        st.session_state.planning = df  # <- stocke le planning dans session_state

        st.success("Planning généré avec succès !")

    except Exception as e:
        st.error(f"Erreur génération planning : {e}")


# FERMETURE CONNEXION
cur.close()
conn.close()
