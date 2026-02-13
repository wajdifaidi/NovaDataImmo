
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import subprocess
import sys
from datetime import datetime
import glob
import re

# Page Config
st.set_page_config(page_title="NovaData Immo - Dashboard", layout="wide")

# Dept Mapping (Common French Departments)
DEPT_MAP = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence", "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes", "09": "Ariège", "10": "Aube",
    "11": "Aude", "12": "Aveyron", "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal",
    "16": "Charente", "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud",
    "2B": "Haute-Corse", "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne",
    "25": "Doubs", "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde", "34": "Hérault",
    "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire", "38": "Isère", "39": "Jura",
    "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire", "44": "Loire-Atlantique",
    "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère", "49": "Maine-et-Loire",
    "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle",
    "55": "Meuse", "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord",
    "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin", "68": "Haut-Rhin", "69": "Rhône",
    "70": "Haute-Saône", "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres",
    "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse",
    "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne",
    "90": "Territoire de Belfort", "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis", "94": "Val-de-Marne",
    "95": "Val-d'Oise", "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion", "976": "Mayotte"
}

# Helpers
def load_promoter_mapping():
    if os.path.exists('promoter_mapping.json'):
        with open('promoter_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def parse_delivery_date(text):
    if not text or not isinstance(text, str):
        return None, "Inconnu"
    
    # Example: "3ème trimestre 2027"
    m = re.search(r'(\d+).*trimestre\s+(\d{4})', text, re.IGNORECASE)
    if m:
        q = m.group(1)
        y = m.group(2)
        return int(y) * 10 + int(q), f"{y}-Q{q}"
    
    # Immediate delivery
    if "immédiate" in text.lower():
        now = datetime.now()
        q = (now.month - 1) // 3 + 1
        return now.year * 10 + q, "Immédiate"
        
    return 9999, text # Fallback for unknown formats

def load_all_scraped_data():
    all_data = []
    files = glob.glob('properties_*.json')
    for f in files:
        promoter_slug = f.replace('properties_', '').replace('.json', '')
        mapping = load_promoter_mapping()
        name = next((k for k, v in mapping.items() if v['slug'] == promoter_slug), promoter_slug)
        
        with open(f, 'r', encoding='utf-8') as jf:
            try:
                items = json.load(jf)
            except:
                continue
                
            for item in items:
                city_name = item.get('city', "N/A")
                dept_num = item.get('dept_num', "N/A")
                
                units = item.get('units', [])
                
                # Robust count of units
                nb_logements = 0
                if units:
                    for u in units:
                        try:
                            nb_logements += int(u.get('nb_unités', 1))
                        except (ValueError, TypeError):
                            nb_logements += 1
                
                if nb_logements == 0 and units:
                    nb_logements = len(units)
                
                total_price = 0
                total_surface = 0
                for u in units:
                    try:
                        p = float(u.get('prix') or 0)
                        s = float(u.get('superficie') or 0)
                        if p > 0 and s > 0:
                            total_price += p
                            total_surface += s
                    except (ValueError, TypeError):
                        continue
                
                avg_price_m2 = (total_price / total_surface) if total_surface > 0 else 0
                
                sort_key, display_date = parse_delivery_date(item.get('livraison'))
                
                all_data.append({
                    "Source": name,
                    "Nom": item.get('name'),
                    "Ville": city_name,
                    "Département": dept_num,
                    "Localisation": f"{city_name} ({dept_num})" if dept_num != "N/A" else city_name,
                    "Statut": item.get('statut') or "N/A",
                    "Livraison": item.get('livraison'),
                    "Livraison_Code": sort_key,
                    "Livraison_Label": display_date,
                    "Nb_Logements": nb_logements,
                    "Prix_m2": avg_price_m2,
                    "Link": item.get('link'),
                    "Date_Scraping": datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
                })
    return pd.DataFrame(all_data)

# Main UI
st.title("🏙️ NovaData Immo")

tab_dash, tab_admin = st.tabs(["📊 Dashboard", "⚙️ Ajouter un promoteur"])

with tab_admin:
    st.header("Gestion des Scrapers")
    mapping = load_promoter_mapping()
    
    if not mapping:
        st.error("Cartographie des promoteurs introuvable.")
    else:
        st.write(f"**{len(mapping)}** promoteurs disponibles.")
        selected_name = st.selectbox("Sélectionner un promoteur", options=sorted(mapping.keys()))
        selected_info = mapping[selected_name]
        
        if st.button(f"🚀 Lancer le Scraper"):
            with st.spinner(f"Scraping en cours..."):
                try:
                    cmd = [sys.executable, "scraper.py", selected_name]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("Scraping terminé !")
                        st.text(result.stdout)
                        st.experimental_rerun()
                    else:
                        st.error(f"Erreur : {result.stderr}")
                except Exception as e:
                    st.error(f"Exception : {e}")

with tab_dash:
    df = load_all_scraped_data()
    
    if df.empty:
        st.warning("Aucune donnée disponible. Allez dans l'onglet Admin.")
    else:
        # Sidebar Filters
        st.sidebar.header("Filtres")
        src_filter = st.sidebar.multiselect("Promoteur", options=sorted(df['Source'].unique()), default=df['Source'].unique())
        
        unique_depts = sorted(df['Département'].unique())
        dept_options = [f"{d} - {DEPT_MAP.get(d, 'Inconnu')}" for d in unique_depts if d != "N/A"]
        dept_selection = st.sidebar.multiselect("Département (Autocomplete)", options=dept_options, default=[])
        
        selected_dept_nums = [opt.split(" - ")[0] for opt in dept_selection] if dept_selection else unique_depts
        
        status_options = sorted(df['Statut'].unique())
        status_selection = st.sidebar.multiselect("Statut (Autocomplete)", options=status_options, default=[])
        selected_status = status_selection if status_selection else status_options
        
        delivery_options = sorted(df['Livraison'].unique())
        delivery_selection = st.sidebar.multiselect("Date de Livraison (Autocomplete)", options=delivery_options, default=[])
        selected_delivery = delivery_selection if delivery_selection else delivery_options
        
        # Filtering logic
        mask = (df['Source'].isin(src_filter)) & (df['Département'].isin(selected_dept_nums)) & (df['Statut'].isin(selected_status)) & (df['Livraison'].isin(selected_delivery))
        filtered_df = df[mask]
            
        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Programmes", len(filtered_df))
        m2.metric("Logements Total", f"{filtered_df['Nb_Logements'].sum():,}")
        
        valid_m2 = filtered_df[filtered_df['Prix_m2'] > 0]
        avg_m2 = valid_m2['Prix_m2'].mean() if not valid_m2.empty else 0
        m3.metric("Prix m² Moyen", f"{avg_m2:,.0f} €")
        
        m4.metric("Dernière MAJ", df['Date_Scraping'].max())
        
        # --- Market Trends Charts ---
        st.subheader("📈 Analytique : Tendances du Marché")
        
        c1, c2 = st.columns(2)
        
        with c1:
            # Curve 1: Housing Supply vs Time
            st.write("**Évolution de l'Offre (Logements / Temps)**")
            if not filtered_df.empty:
                time_trend = filtered_df.groupby(['Livraison_Code', 'Livraison_Label'])['Nb_Logements'].sum().reset_index()
                time_trend = time_trend.sort_values('Livraison_Code')
                fig_time = px.line(time_trend, x='Livraison_Label', y='Nb_Logements', markers=True, 
                                 labels={'Livraison_Label': 'Date de Livraison', 'Nb_Logements': 'Nombre de Logements'},
                                 title="Tendance d'ouverture des programmes")
                fig_time.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("Données insuffisantes pour la courbe temporelle.")
                
        with c2:
            # Curve 2: Housing Supply vs Department
            st.write("**Répartition par Département (Logements / Dept)**")
            if not filtered_df.empty:
                dept_trend = filtered_df.groupby('Département')['Nb_Logements'].sum().reset_index()
                dept_trend = dept_trend.sort_values('Nb_Logements', ascending=False)
                # Add names for clarity in chart
                dept_trend['Label'] = dept_trend['Département'].apply(lambda x: f"{x} - {DEPT_MAP.get(x, 'N/A')}")
                fig_dept = px.bar(dept_trend, x='Label', y='Nb_Logements', 
                                labels={'Label': 'Département', 'Nb_Logements': 'Nombre de Logements'},
                                title="Forte demande par zone géographique",
                                color='Nb_Logements', color_continuous_scale='Viridis')
                st.plotly_chart(fig_dept, use_container_width=True)
            else:
                st.info("Données insuffisantes pour la répartition géographique.")
            
        # Data View
        st.subheader("📋 Détails des Programmes")
        st.dataframe(filtered_df.drop(columns=['Date_Scraping', 'Ville', 'Département', 'Livraison_Code', 'Livraison_Label']), use_container_width=True)
        
        st.download_button("📥 Exporter CSV", filtered_df.to_csv(index=False).encode('utf-8-sig'), "export_immo.csv", "text/csv")
