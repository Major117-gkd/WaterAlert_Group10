import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="WaterAlert | Professional Dashboard",
        page_icon="🚰",
        layout="wide"
    )
    load_css()

    db = DBManager()

    # --- Header ---
    st.markdown("""
        <div class="main-header">
            <h1>🚰 WaterAlert Dashboard</h1>
            <p>Système intelligent de suivi et de gestion des fuites d'eau</p>
        </div>
    """, unsafe_allow_html=True)

    # Load data
    leaks = db.get_all_leaks()
    if not leaks:
        st.info("Aucun signalement pour le moment.")
        st.stop()

    # Data Processing
    num_cols = len(leaks[0])
    if num_cols == 12:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Adresse', 'Sévérité', 'IA Sévérité', 'Technicien', 'Statut', 'Date']
    elif num_cols == 11:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Adresse', 'Sévérité', 'Technicien', 'Statut', 'Date']
    elif num_cols == 10:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Adresse', 'Sévérité', 'Statut', 'Date']
    else:
        cols = ['ID', 'User ID', 'Citoyen', 'Photo', 'Lat', 'Lon', 'Statut', 'Date']

    df = pd.DataFrame(leaks, columns=cols[:num_cols])

    # --- Sidebar Filters ---
    st.sidebar.markdown("## ⚙️ Paramètres")
    st.sidebar.subheader("🔍 Filtres")
    
    status_options = df['Statut'].unique().tolist()
    status_filter = st.sidebar.multiselect(
        "Filtrer par statut",
        options=status_options,
        default=status_options
    )

    severity_options = df['Sévérité'].unique().tolist() if 'Sévérité' in df.columns else []
    if severity_options:
        severity_filter = st.sidebar.multiselect(
            "Filtrer par sévérité",
            options=severity_options,
            default=severity_options
        )
        filtered_df = df[(df['Statut'].isin(status_filter)) & (df['Sévérité'].isin(severity_filter))]
    else:
        filtered_df = df[df['Statut'].isin(status_filter)]

    # Heatmap Toggle
    st.sidebar.divider()
    show_heatmap = st.sidebar.checkbox("🔥 Mode Carte de Chaleur", value=False)

    # Export Section in Sidebar
    st.sidebar.divider()
    st.sidebar.subheader("📥 Exportation")
    # Use utf-8-sig (with BOM) and semicolon for better Excel compatibility
    csv = filtered_df.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.sidebar.download_button(
        label="Télécharger les données (CSV)",
        data=csv,
        file_name=f"WaterAlert_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime='text/csv',
    )

    # --- Metrics Row ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Signalements", len(df))
    m2.metric("📦 En attente", len(df[df['Statut'] == 'Signalé']))
    m3.metric("🛠️ En cours", len(df[df['Statut'] == 'En cours']))
    m4.metric("✅ Réparés", len(df[df['Statut'] == 'Réparé']))

    st.markdown("---")

    # --- Main Content: Map and Analysis ---
    content_tab, analytics_tab, data_tab = st.tabs([
        "📊 Vue Opérationnelle", 
        "📈 Analyses Stratégiques",
        "📋 Données Brutes"
    ])

    with content_tab:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📍 Carte Interactive")
            if not filtered_df.empty:
                m = folium.Map(location=[filtered_df['Lat'].mean(), filtered_df['Lon'].mean()], zoom_start=12)
                
                if show_heatmap:
                    # Severity weights for HeatMap
                    weights = {
                        'Élevée': 3.0,
                        'Moyenne': 2.0,
                        'Petite': 1.0,
                        'Inconnue': 1.0
                    }
                    heat_data = [
                        [row['Lat'], row['Lon'], weights.get(row.get('Sévérité', 'Inconnue'), 1.0)] 
                        for _, row in filtered_df.iterrows()
                    ]
                    HeatMap(heat_data, radius=15, blur=20, min_opacity=0.5).add_to(m)
                else:
                    for _, row in filtered_df.iterrows():
                        color = 'red' if row['Statut'] == 'Signalé' else 'orange' if row['Statut'] == 'En cours' else 'green'
                        folium.Marker(
                            [row['Lat'], row['Lon']],
                            popup=f"Report #{row['ID']}",
                            tooltip=f"{row.get('Adresse', 'Signalement #' + str(row['ID']))}",
                            icon=folium.Icon(color=color, icon='info-sign')
                        ).add_to(m)
                
                st_folium(m, height=500, width='stretch')
            else:
                st.warning("Aucune donnée à afficher sur la carte avec les filtres actuels.")

        with col2:
            st.subheader("📋 Signalements Récents")
            # Scrollable container for cards (simulated with fixed height if possible, but streamlit is reactive)
            for _, row in filtered_df.iterrows():
                with st.expander(f"📌 Fuite #{row['ID']} - {row['Statut']}"):
                    if os.path.exists(row['Photo']):
                        st.image(row['Photo'], use_container_width=True)
                    
                    st.markdown(f"""
                    **👤 Citoyen:** {row['Citoyen']}  
                    **📍 Adresse:** {row.get('Adresse', 'N/A')}  
                    **⏳ Date:** {row.get('Date', 'N/A')}
                    """)
                    
                    severity = row.get('Sévérité', 'Inconnue')
                    ai_severity = row.get('IA Sévérité', 'Inconnue')
                    
                    st.markdown(f"**👤 Citoyen:** {severity}")
                    if ai_severity != severity and ai_severity != "Inconnue":
                        st.markdown(f"**🤖 IA (Vérification):** {ai_severity}")

                    # Technician and Status Update
                    col_tech, col_stat = st.columns(2)
                    
                    with col_tech:
                        current_tech = row.get('Technicien') if pd.notna(row.get('Technicien')) else ""
                        new_tech = st.text_input(
                            "Technicien assigné",
                            value=current_tech,
                            key=f"tech_{row['ID']}"
                        )
                    
                    with col_stat:
                        new_status = st.selectbox(
                            "Statut",
                            options=['Signalé', 'En cours', 'Réparé'],
                            index=['Signalé', 'En cours', 'Réparé'].index(row['Statut']),
                            key=f"status_{row['ID']}"
                        )
                    
                    if new_status != row['Statut'] or new_tech != current_tech:
                        db.update_leak_status(row['ID'], new_status, technician=new_tech)
                        st.success("Mis à jour !")
                        st.rerun()

    with analytics_tab:
        st.subheader("📊 Analyse de la Performance")
        
        # Row 1: Status and Severity
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### Répartition par Statut")
            status_counts = filtered_df['Statut'].value_counts()
            fig_status = px.pie(
                values=status_counts.values, 
                names=status_counts.index,
                color=status_counts.index,
                color_discrete_map={'Signalé': '#EF4444', 'En cours': '#F59E0B', 'Réparé': '#10B981'},
                hole=0.4
            )
            fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)
            
        with c2:
            st.markdown("##### Sévérité des Signalements")
            if 'Sévérité' in filtered_df.columns:
                sev_counts = filtered_df['Sévérité'].value_counts()
                fig_sev = px.bar(
                    x=sev_counts.index, 
                    y=sev_counts.values,
                    color=sev_counts.index,
                    title=None,
                    labels={'x': 'Sévérité', 'y': 'Nombre'}
                )
                fig_sev.update_layout(showlegend=False, margin=dict(t=20, b=20, l=0, r=0))
                st.plotly_chart(fig_sev, use_container_width=True)
            else:
                st.info("Données de sévérité indisponibles.")

        st.markdown("---")
        
        # Row 2: Temporal Trends
        st.markdown("##### ⏳ Évolution temporelle des signalements")
        if 'Date' in filtered_df.columns:
            # Simple daily grouping
            filtered_df['Date_parsed'] = pd.to_datetime(filtered_df['Date']).dt.date
            trend_df = filtered_df.groupby('Date_parsed').size().reset_index(name='Nombre')
            fig_trend = px.line(
                trend_df, x='Date_parsed', y='Nombre',
                markers=True,
                line_shape='spline',
                color_discrete_sequence=['#0099CC']
            )
            fig_trend.update_layout(margin=dict(t=20, b=20, l=0, r=0), xaxis_title="Date", yaxis_title="Signalements")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Données temporelles insuffisantes.")

    with data_tab:
        st.subheader("📊 Registre des Interventions")
        st.dataframe(filtered_df, width='stretch', height=600)

if __name__ == "__main__":
    main()
