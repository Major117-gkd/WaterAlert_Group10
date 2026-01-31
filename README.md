# WaterAlert 🚰

WaterAlert est une solution professionnelle de gestion et de monitoring des fuites d'eau. Elle combine un Bot Telegram pour le signalement citoyen et un tableau de bord analytique avancé pour les gestionnaires.

## 🚀 Fonctionnalités Professionnelles

### 📊 Business Intelligence (BI)
- **Tableau de bord interactif** : Visualisation en temps réel des indicateurs clés (KPIs).
- **Analyses Stratégiques** : Graphiques Plotly pour le suivi des tendances, répartition par statut et sévérité.
- **Exportation de données** : Extraction des signalements au format CSV pour reporting externe.

### 🗺️ Intelligence Géographique
- **Cartographie interactive** : Visualisation précise de chaque incident.
- **Carte de chaleur (Heatmap)** : Identification des zones critiques pondérée par la sévérité des fuites.

### 🛠️ Gestion Opérationnelle
- **Assignation des techniciens** : Suivi nominatif des interventions.
- **Cycle de vie des incidents** : Gestion complète des statuts (Signalé, En cours, Réparé).

## 📂 Structure du Projet

```
WaterAlert/
├── data/               # Base de données SQLite (Persistence)
├── src/
│   ├── database/       # Gestionnaire de base de données
│   ├── bot/            # Intelligence du Bot Telegram
│   └── dashboard/      # Frontend Streamlit & assets CSS
├── streamlit_app.py    # Point d'entrée principal (Déploiement)
├── verify_setup.py     # Script de diagnostic technique
├── .env                # Configuration sécurisée (Token Bot)
└── requirements.txt    # Dépendances du projet
```

## 🛠️ Installation & Configuration

1. **Préparation de l'environnement** :
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configuration du Bot** :
   - Créez votre bot via [@BotFather](https://t.me/botfather).
   - Renseignez votre token dans le fichier `.env` : `TELEGRAM_BOT_TOKEN=...`.

3. **Vérification du système** :
   ```bash
   python verify_setup.py
   ```

## 🖥️ Utilisation

### Lancer le Service de Signalement (Bot)
```bash
python src/bot/telegram_bot.py
```

### Lancer la Console d'Administration (Dashboard)
```bash
python -m streamlit run streamlit_app.py
```

## 🛡️ Sécurité & Déploiement
- Le projet inclut un fichier `.gitignore` pré-configuré pour protéger vos données sensibles.
- Compatible avec un déploiement sécurisé sur **Streamlit Cloud**.
