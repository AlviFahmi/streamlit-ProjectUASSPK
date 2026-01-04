import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="SPK Penilaian Kinerja Atasan",
    layout="wide"
)

st.title("📊 Sistem Pendukung Keputusan Penilaian Kinerja Atasan")
st.markdown("**Metode: SAW & Copeland Score (Hybrid)**")

uploaded_file = st.file_uploader(
    "📂 Upload Dataset Penilaian (CSV)",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # Mapping nama kolom 
    df = df.rename(columns={
    "C1": "Kepemimpinan",
    "C2": "Komunikasi",
    "C3": "Kerjasama",
    "C4": "Sikap Profesional",
    "C5": "Arah & Pengambilan Keputusan"
})

    st.subheader("📋 Tabel Keputusan")
    st.dataframe(df, use_container_width=True)

    # ======================
    # Alternatif & Kriteria
    # ======================
    alternatif = df["Atasan"]
    kriteria = [
    "Kepemimpinan",
    "Komunikasi",
    "Kerjasama",
    "Sikap Profesional",
    "Arah & Pengambilan Keputusan"
]
    # Paksa numerik
    for c in kriteria:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df[kriteria] = df[kriteria].fillna(0)

    # ======================
    # Bobot Kriteria
    # ======================
    st.subheader("⚖️ Bobot Kriteria")

    bobot_list = [0.30, 0.20, 0.15, 0.15, 0.20]

    bobot_df = pd.DataFrame({
        "Kriteria": kriteria,
        "Bobot": bobot_list
    })
    st.table(bobot_df)

    if round(sum(bobot_list), 2) != 1:
        st.error("❌ Total bobot harus = 1")
        st.stop()

    # ======================
    # Normalisasi SAW
    # ======================
    st.subheader("🔢 Normalisasi SAW")

    norm_df = df.copy()
    for c in kriteria:
        max_val = df[c].max()
        norm_df[c] = df[c] / max_val if max_val != 0 else 0

    st.dataframe(norm_df, use_container_width=True)

    # ======================
    # Nilai Preferensi SAW
    # ======================
    st.subheader("⭐ Nilai Preferensi SAW")

    pref_values = []

    for i in range(len(df)):
        total = 0
        for j, c in enumerate(kriteria):
            total += norm_df.loc[i, c] * bobot_list[j]
        pref_values.append(total)

    saw_df = pd.DataFrame({
        "Atasan": alternatif,
        "Nilai Preferensi SAW": pref_values
    }).sort_values(
        by="Nilai Preferensi SAW",
        ascending=False
    ).reset_index(drop=True)

    st.dataframe(saw_df, use_container_width=True)

    # ======================
    # Copeland Score
    # ======================
    st.subheader("⚔️ Copeland Score")

    scores = saw_df["Nilai Preferensi SAW"].values
    names = saw_df["Atasan"].values

    wins = {n: 0 for n in names}
    losses = {n: 0 for n in names}

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
    }).sort_values(
        by="Copeland Score",
        ascending=False
    ).reset_index(drop=True)

    st.dataframe(copeland_df, use_container_width=True)

    st.subheader("📈 Grafik Ranking Copeland Score")
    st.bar_chart(copeland_df.set_index("Atasan")["Copeland Score"])

else:
    st.info("⬆️ Silakan upload file CSV untuk memulai.")
