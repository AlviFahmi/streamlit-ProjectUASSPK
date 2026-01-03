import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SPK Penilaian Kinerja Atasan", layout="wide")

st.title("📊 Sistem Pendukung Keputusan Penilaian Kinerja Atasan")
st.write("Metode: **SAW & Copeland Score (Hybrid)**")

# ======================
# Upload Dataset
# ======================
uploaded_file = st.file_uploader("Upload Dataset Penilaian (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📋 Tabel Keputusan")
    st.dataframe(df)

    alternatif = df["Atasan"]
    kriteria = df.columns[1:]

    # ======================
    # Bobot Kriteria
    # ======================
    st.subheader("⚖️ Bobot Kriteria")
    weights = {
        "Kepemimpinan": 0.30,
        "Komunikasi": 0.20,
        "Kerjasama": 0.15,
        "Sikap Profesional": 0.15,
        "Arah & Pengambilan Keputusan": 0.20
    }

    bobot_df = pd.DataFrame({
        "Kriteria": weights.keys(),
        "Bobot": weights.values()
    })
    st.table(bobot_df)

    # ======================
    # Normalisasi SAW
    # ======================
    st.subheader("🔢 Normalisasi SAW")
    norm_df = df.copy()

    for c in kriteria:
        norm_df[c] = df[c] / df[c].max()

    st.dataframe(norm_df)

    # ======================
    # Nilai Preferensi SAW
    # ======================
    st.subheader("⭐ Nilai Preferensi SAW")
    pref_values = []

    for i in range(len(df)):
        total = 0
        for c in kriteria:
            total += norm_df.loc[i, c] * weights[c]
        pref_values.append(total)

    result_df = pd.DataFrame({
        "Atasan": alternatif,
        "Nilai Preferensi": pref_values
    }).sort_values(by="Nilai Preferensi", ascending=False)

    st.dataframe(result_df)

    # ======================
    # Copeland Score
    # ======================
    st.subheader("⚔️ Copeland Score")
    scores = result_df["Nilai Preferensi"].values
    names = result_df["Atasan"].values

    wins = {name: 0 for name in names}
    losses = {name: 0 for name in names}

    for i in range(len(scores)):
        for j in range(len(scores)):
            if i != j:
                if scores[i] > scores[j]:
                    wins[names[i]] += 1
                elif scores[i] < scores[j]:
                    losses[names[i]] += 1

    copeland_df = pd.DataFrame({
        "Atasan": names,
        "Menang": [wins[n] for n in names],
        "Kalah": [losses[n] for n in names],
        "Copeland Score": [wins[n] - losses[n] for n in names]
    }).sort_values(by="Copeland Score", ascending=False)

    st.dataframe(copeland_df)

    # ======================
    # Grafik Ranking
    # ======================
    st.subheader("📈 Grafik Ranking Copeland Score")
    st.bar_chart(copeland_df.set_index("Atasan")["Copeland Score"])

else:
    st.info("Silakan upload file CSV untuk memulai.")
