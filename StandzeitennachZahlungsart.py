import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Funktion zum Laden der Excel-Datei
@st.cache_data
def load_excel_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Datei: {e}")
        return None

# Hilfsfunktion zum Parsen von "1 Stunde 5 Minuten 3 Sekunden"
def parse_standzeit(zeit_string):
    if pd.isna(zeit_string):
        return None
    stunden = minuten = sekunden = 0
    match_stunden = re.search(r"(\d+)\s*Stunde", zeit_string)
    match_minuten = re.search(r"(\d+)\s*Minute", zeit_string)
    match_sekunden = re.search(r"(\d+)\s*Sekunde", zeit_string)
    if match_stunden:
        stunden = int(match_stunden.group(1))
    if match_minuten:
        minuten = int(match_minuten.group(1))
    if match_sekunden:
        sekunden = int(match_sekunden.group(1))
    return stunden + minuten / 60 + sekunden / 3600

# Streamlit-Seitenlayout
st.set_page_config(page_title="Analyse Standzeiten", layout="wide")
st.title("Analyse Standzeiten")

# Datei-Upload
uploaded_file = st.file_uploader("📁 Bereinigte Excel-Datei hochladen", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = load_excel_file(uploaded_file)

    if df is not None:
        st.subheader("Originaldaten nach Datenformatanpassung")

        df = df.copy()
        df['Gestartet'] = pd.to_datetime(df['Gestartet'], errors='coerce')
        df['Beendet'] = pd.to_datetime(df['Beendet'], errors='coerce')
        df['Verbrauch_kWh'] = pd.to_numeric(df['Verbrauch (kWh)'], errors='coerce')
        df['Kosten_EUR'] = pd.to_numeric(df['Kosten'], errors='coerce')
        df['Ladezeit_h'] = (df['Beendet'] - df['Gestartet']).dt.total_seconds() / 3600.0
        df['P_Schnitt'] = df['Verbrauch_kWh'] / df['Ladezeit_h']

        # Standzeit als Stundenwert berechnen
        df['Standzeit_h'] = df['Standzeit'].apply(parse_standzeit)

        df['Jahr'] = df['Beendet'].dt.year
        df['Monat_num'] = df['Beendet'].dt.month
        df['Tag'] = df['Beendet'].dt.day
        df['Stunde'] = df['Beendet'].dt.hour

        st.write(df, use_container_width=True)

        grouped = df.groupby('Standortname', as_index=False).agg(
            Verbrauch_kWh_mean=('Verbrauch_kWh', 'mean'),
            Standzeit_h=('Standzeit_h', 'mean'),
            Anzahl_Ladevorgaenge=('Verbrauch_kWh', 'count')
        )
        st.subheader("🔢 Allgemeine KPIs nach Standort")
        st.dataframe(grouped, use_container_width=True)

        groupedby_authtyp = df.groupby('Auth. Typ', as_index=False).agg(
            Ladezeit_h=('Ladezeit_h', 'mean'),
            Verbrauch_kWh_mean=('Verbrauch_kWh', 'mean')
        )

        st.write(groupedby_authtyp, use_container_width=True)
