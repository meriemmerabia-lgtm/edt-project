import os
from faker import Faker
import psycopg2
import random
import streamlit as st
from datetime import datetime, timedelta

fake = Faker()
fake.unique.clear()

conn = psycopg2.connect(
    host="db.ryzlenworqjmdgkanfcj.supabase.co",
    database="postgres",
    user="postgres",
    password="Etd2026!Secure",
    port=5432

)
cursor = conn.cursor()

# 1. Départements
departements = ["Informatique", "Maths", "Physique", "Chimie", "Biologie", "Economie", "Droit"]
for dept in departements:
    cursor.execute("""
        INSERT INTO departements (nom)
        VALUES (%s)
        ON CONFLICT (nom) DO NOTHING
        RETURNING id;
    """, (dept,))
conn.commit()

cursor.execute("SELECT id, nom FROM departements;")
dept_ids = cursor.fetchall()

# 2. Formations
formations_par_dept = 30
for dept_id, dept_name in dept_ids:
    for i in range(1, formations_par_dept + 1):
        nom_formation = f"{dept_name} Formation {i}"
        nb_modules = random.randint(6, 9)
        cursor.execute("""
            INSERT INTO formations (nom, dept_id, nb_modules)
            VALUES (%s, %s, %s)
            ON CONFLICT (nom) DO NOTHING
        """, (nom_formation, dept_id, nb_modules))
conn.commit()

cursor.execute("SELECT id, nom, dept_id FROM formations;")
formation_ids = cursor.fetchall()

# 3. Étudiants (~13000)
nb_etudiants_total = 13000
etudiants_par_formation = nb_etudiants_total // len(formation_ids)
for f_id, f_name, f_dept in formation_ids:
    for _ in range(etudiants_par_formation):
        nom = fake.last_name()
        prenom = fake.first_name()
        niveau = random.choice(["L1", "L2", "L3", "M1", "M2"])
        classe = random.choice(["A", "B", "C"])
        cursor.execute("""
            INSERT INTO etudiants (nom, prenom, formation_id, niveau, classe)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, prenom, f_id, niveau, classe))
conn.commit()

cursor.execute("SELECT id, formation_id FROM etudiants;")
etudiants = cursor.fetchall()

# 4. Modules
modules = []
for f_id, f_name, f_dept in formation_ids:
    nb_modules = random.randint(6, 9)
    for i in range(nb_modules):
        nom_module = f"{f_name} Module {i+1}"
        credits = random.choice([3, 4, 5])
        cursor.execute("""
            INSERT INTO modules (nom, credits, formation_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nom_module, credits, f_id))
        module_id = cursor.fetchone()[0]
        modules.append((module_id, f_id))
conn.commit()

# 5. Professeurs
professeurs = []
for dept_id, dept_name in dept_ids:
    for i in range(15):
        nom = fake.unique.last_name()
        specialite = f"Spécialité {i+1}"
        cursor.execute("""
            INSERT INTO professeurs (nom, dept_id, specialite)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nom, dept_id, specialite))
        prof_id = cursor.fetchone()[0]
        professeurs.append((prof_id, dept_id))
conn.commit()

# 6. Salles
salles = []
capacites_possibles = [20, 30, 50, 100]
salles_par_dept = 5
for dept_id, dept_name in dept_ids:
    for i in range(1, salles_par_dept+1):
        batiment = f"Batiment {random.randint(1,5)}"
        nom = f"{dept_name} Salle {i} ({batiment})"
        capacite = random.choice(capacites_possibles)
        type_salle = random.choice(["Amphi", "Salle de TP"])
        cursor.execute("""
            INSERT INTO lieu_examen (nom, capacite, type, batiment, dept_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (nom, capacite, type_salle, batiment, dept_id))
        salle_id = cursor.fetchone()[0]
        salles.append((salle_id, dept_id))
conn.commit()

# 7. Examens
for module_id, f_id in modules:
    dept_id = next(f_dept for fid, f_name, f_dept in formation_ids if fid == f_id)
    prof_ids_dept = [pid for pid, p_dept in professeurs if p_dept == dept_id]
    salle_dept = [s_id for s_id, s_dept in salles if s_dept == dept_id]

    prof_id = random.choice(prof_ids_dept)
    salle_id = random.choice(salle_dept)
    date_heure = fake.date_time_between(start_date="now", end_date="+30d")
    duree = random.choice([60, 90, 120])

    cursor.execute("""
        INSERT INTO examens (module_id, prof_id, salle_id, date_heure, duree_minutes)
        VALUES (%s, %s, %s, %s, %s)
    """, (module_id, prof_id, salle_id, date_heure, duree))
conn.commit()

# 8. Inscriptions
for etu_id, f_id in etudiants:
    modules_de_form = [m_id for m_id, mod_fid in modules if mod_fid == f_id]
    modules_sample = modules_de_form if len(modules_de_form) <= 6 else random.sample(modules_de_form, 6)
    for mod_id in modules_sample:
        note = round(random.uniform(0, 20), 2)
        cursor.execute("""
            INSERT INTO inscriptions (etudiant_id, module_id, note)
            VALUES (%s, %s, %s)
        """, (etu_id, mod_id, note))
conn.commit()

cursor.close()
conn.close()
print("Base de données remplie avec succès !")
