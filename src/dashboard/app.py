import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager

def main():
    st.set_page_config(page_title="WaterAlert Dashboard", layout="wide")

    db = DBManager()

    st.title("🚰 WaterAlert - Suivi des Fuites")

    # Load data safely
    leaks = db.get_all_leaks()
    if not leaks:
        st.info("Aucun signalement pour le moment.")
        st.stop()

    # Handle different database versions gracefully
    num_cols = len(leaks[0])
    if num_cols == 11:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Adresse', 'Sévérité', 'Technicien', 'Statut', 'Date']
    elif num_cols == 10:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Adresse', 'Sévérité', 'Statut', 'Date']
    else:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Statut', 'Date']

    df = pd.DataFrame(leaks, columns=cols[:num_cols])

    # Sidebar filter
    st.sidebar.header("Filtres")
    status_filter = st.sidebar.multiselect(
        "Filtrer par statut",
        options=df['Statut'].unique(),
        default=df['Statut'].unique()
    )

    filtered_df = df[df['Statut'].isin(status_filter)]

    # Main Layout: Map and List
    m_col, l_col = st.columns([2, 1])

    with m_col:
        st.subheader("📍 Carte des signalements")
        if not filtered_df.empty:
            m = folium.Map(location=[filtered_df['Lat'].mean(), filtered_df['Lon'].mean()], zoom_start=12)
            for _, row in filtered_df.iterrows():
                # Marker color
                color = 'red' if row['Statut'] == 'Signalé' else 'orange' if row['Statut'] == 'En cours' else 'green'
                folium.Marker(
                    [row['Lat'], row['Lon']],
                    popup=f"Fuite #{row['ID']} - {row['Statut']}",
                    tooltip=f"{row.get('Adresse', 'Signalement #' + str(row['ID']))}",
                    icon=folium.Icon(color=color)
                ).add_to(m)
            st_folium(m, width=800, height=500)
        else:
            st.warning("Aucun point à afficher.")

    with l_col:
        st.subheader("📋 Liste des signalements")
        for _, row in filtered_df.iterrows():
            with st.expander(f"Report #{row['ID']} - {row['Statut']}"):
                if os.path.exists(row['Photo']):
                    st.image(row['Photo'], use_container_width=True)
                
                st.write(f"**Par:** {row['Citoyen']}")
                st.write(f"**Adresse:** {row.get('Adresse', 'N/A')}")
                st.write(f"**Sévérité:** {row.get('Sévérité', 'N/A')}")
                
                # Simple Status Update
                new_status = st.selectbox(
                    "Mettre à jour le statut",
                    options=['Signalé', 'En cours', 'Réparé'],
                    index=['Signalé', 'En cours', 'Réparé'].index(row['Statut']),
                    key=f"status_{row['ID']}"
                )
                
                if new_status != row['Statut']:
                    db.update_leak_status(row['ID'], new_status)
                    st.success(f"Statut mis à jour pour #{row['ID']}")
                    st.rerun()

    st.divider()
    st.subheader("📊 Données brutes")
    st.dataframe(filtered_df, use_container_width=True)

if __name__ == "__main__":
    main()
