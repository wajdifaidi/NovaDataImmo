import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import os

# Page Config
st.set_page_config(page_title="NovaData Immo - Dashboard", layout="wide")

st.title("🏙️ NovaData Immo : Projets Résidentiels")

# Load Data
@st.cache_data
def load_data():
    if os.path.exists('data.csv'):
        df = pd.read_csv('data.csv')
        # Ensure correct types
        return df
    return pd.DataFrame(columns=["Type", "Nom", "Statut", "Localisation", "Nb_Logements", "Prix_m2", "Date_Scraping"])


df = load_data()

if df.empty:
    st.warning("Aucune donnée trouvée. Veuillez lancer le scraper d'abord.")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Filtres & Actions")
    type_filter = st.sidebar.multiselect("Type de bien", options=sorted(df['Type'].unique()), default=df['Type'].unique())
    status_filter = st.sidebar.multiselect("Statut du programme", options=sorted(df['Statut'].unique()), default=df['Statut'].unique())
    
    # Filter Data
    filtered_df = df[(df['Statut'].isin(status_filter)) & (df['Type'].isin(type_filter))]
    
    # Download Button (Best for printing large tables)
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(
        label="📥 Télécharger le Rapport (CSV)",
        data=csv,
        file_name='rapport_immobilier.csv',
        mime='text/csv',
    )
    
    print_mode = st.sidebar.checkbox("🖨️ Mode Impression")
    
def render_charts(data):
    st.subheader("Analyses")
    c1, c2 = st.columns(2)
    with c1:
        fig_status = px.pie(data, names='Statut', title="Répartition par Statut", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_status, use_container_width=True)
    with c2:
        if 'Prix_m2' in data.columns:
            fig_m2 = px.box(data, x='Statut', y='Prix_m2', title="Prix au m² par Statut", color='Statut')
            st.plotly_chart(fig_m2, use_container_width=True)
        else:
            fig_price = px.histogram(data, x='Prix', title="Distribution des Prix", nbins=20)
            st.plotly_chart(fig_price, use_container_width=True)

# --- Print Mode Logic ---
if print_mode:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            .main .block-container { padding-top: 2rem !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("# 📄 Rapport Immobilière - Nexity")
    st.write(f"Généré le: {df['Date_Scraping'].max()}")
    st.write(f"**Nombre de programmes :** {len(filtered_df)}")
    
    pk1, pk2, pk3 = st.columns(3)
    pk1.metric("Nb Programmes", len(filtered_df))
    pk2.metric("Total Logements", f"{filtered_df['Nb_Logements'].sum():,.0f}" if 'Nb_Logements' in filtered_df.columns else "0")
    pk3.metric("Prix m² Moyen", f"{filtered_df['Prix_m2'].mean():.0f} €" if 'Prix_m2' in filtered_df.columns and not filtered_df.empty else "0 €")
    
    st.write("---")
    render_charts(filtered_df)
    
    st.write("---")
    st.subheader("Détails des Programmes")
    st.table(filtered_df[["Type", "Nom", "Statut", "Localisation", "Nb_Logements", "Prix_m2"]])
    st.stop()

# --- Main View (Non-Print) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nb Programmes", len(filtered_df))
col2.metric("Total Logements", f"{filtered_df['Nb_Logements'].sum():,.0f}" if 'Nb_Logements' in filtered_df.columns else "0")
col3.metric("Prix m² Moyen", f"{filtered_df['Prix_m2'].mean():.0f} €" if 'Prix_m2' in filtered_df.columns and not filtered_df.empty else "0 €")
col4.metric("Dernière MAJ", df['Date_Scraping'].max())

render_charts(filtered_df)

st.subheader("Détails des Programmes")
st.dataframe(filtered_df, use_container_width=True)
