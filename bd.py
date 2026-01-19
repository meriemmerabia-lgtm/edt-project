import psycopg2
import streamlit as st

def get_connection():
    cfg = st.secrets["postgres"]  # utiliser Streamlit secrets
    return psycopg2.connect(
        host=cfg["host"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"],
        sslmode="require"
    )
