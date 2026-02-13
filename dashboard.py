
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import subprocess
import sys
from datetime import datetime
import glob

# Page Config
st.set_page_config(page_title="NovaData Immo - Dashboard", layout="wide")

# Helpers
def load_promoter_mapping():
    if os.path.exists('promoter_mapping.json'):
        with open('promoter_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_all_scraped_data():
    all_data = []
    files = glob.glob('properties_*.json')
    for f in files:
        promoter_slug = f.replace('properties_', '').replace('.json', '')
        # Get actual promoter name from mapping if possible
        mapping = load_promoter_mapping()
        name = next((k for k, v in mapping.items() if v['slug'] == promoter_slug), promoter_slug)
        
        with open(f, 'r', encoding='utf-8') as jf:
            items = json.load(jf)
            for item in items:
                # Basic flattening for dashboard
                city_name = item.get('city', {}).get('name') if isinstance(item.get('city'), dict) else item.get('city')
                
                # Calculate aggregate metrics for the program
                units = item.get('units', [])
                nb_logements = len(units)
                avg_price = 0
                if units:
                    prices = [u.get('prix') for u in units if u.get('prix')]
                    if prices:
                        avg_price = sum(prices) / len(prices)
                
                all_data.append({
                    "Source": name,
                    "Nom": item.get('name'),
                    "Localisation": f"{city_name} ({item.get('cp')})",
                    "Livraison": item.get('livraison'),
                    "Nb_Logements": nb_logements,
                    "Prix_Moyen": avg_price,
                    "Link": item.get('link'),
                    "Date_Scraping": datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
                })
    return pd.DataFrame(all_data)

# Main UI
st.title("🏙️ NovaData Immo")

tab_dash, tab_admin = st.tabs(["📊 Dashboard", "⚙️ Admin Scraper"])

with tab_admin:
    st.header("Lancement des Scrapers")
    mapping = load_promoter_mapping()
    
    if not mapping:
        st.error("Cartographie des promoteurs introuvable. Veuillez d'abord scanner les partenaires.")
    else:
        st.write(f"**{len(mapping)}** promoteurs disponibles pour le scraping universel.")
        
        selected_name = st.selectbox("Sélectionner un promoteur à scraper", options=sorted(mapping.keys()))
        selected_info = mapping[selected_name]
        
        st.info(f"ID: {selected_info['id']} | Slug: {selected_info['slug']}")
        
        if st.button(f"Lancer le Scraper pour {selected_name}"):
            with st.spinner(f"Scraping de {selected_name} en cours..."):
                try:
                    # Run scraper.py as a subprocess
                    cmd = [sys.executable, "scraper.py", selected_name]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success(f"Scraping terminé pour {selected_name} !")
                        st.text(result.stdout)
                    else:
                        st.error(f"Erreur lors du scraping : {result.stderr}")
                except Exception as e:
                    st.error(f"Exception : {e}")

with tab_dash:
    df = load_all_scraped_data()
    
    if df.empty:
        st.warning("Aucune donnée disponible. Allez dans l'onglet Admin pour lancer un scraper.")
    else:
        # Sidebar Filters
        st.sidebar.header("Filtres")
        src_filter = st.sidebar.multiselect("Promoteur", options=df['Source'].unique(), default=df['Source'].unique())
        loc_filter = st.sidebar.multiselect("Localisation", options=sorted(df['Localisation'].unique()))
        
        filtered_df = df[df['Source'].isin(src_filter)]
        if loc_filter:
            filtered_df = filtered_df[filtered_df['Localisation'].isin(loc_filter)]
            
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Programmes Total", len(filtered_df))
        m2.metric("Promoteurs Actifs", len(filtered_df['Source'].unique()))
        m3.metric("Prix Moyen Estimé", f"{filtered_df['Prix_Moyen'].mean():,.0f} €" if not filtered_df.empty else "0 €")
        
        # Charts
        st.subheader("Analyses")
        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(filtered_df, names='Source', title="Répartition des programmes par promoteur")
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            fig_hist = px.histogram(filtered_df, x='Prix_Moyen', title="Distribution des prix moyens des programmes", nbins=20)
            st.plotly_chart(fig_hist, use_container_width=True)
            
        # Data View
        st.subheader("Détails des Programmes")
        st.dataframe(filtered_df, use_container_width=True)
        
        if st.button("Tout exporter en CSV"):
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Télécharger CSV", csv, "export_immo.csv", "text/csv")
