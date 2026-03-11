# WaterAlert 🚰

WaterAlert est une solution professionnelle de gestion et de monitoring des fuites d'eau. Elle combine un Bot Telegram pour le signalement citoyen, un tableau de bord analytique avancé propulsé par l'IA et une API REST.

## 🚀 Fonctionnalités Professionnelles

### 📊 Business Intelligence (BI) & Analyses

- **Tableau de bord interactif** : Visualisation en temps réel des indicateurs clés (KPIs).
- **Analyses Stratégiques** : Graphiques Plotly pour le suivi des tendances et de la performance.
- **Exportation de données** : Download des données filtrées en CSV ou PDF (Rapport d'intervention).

### 🧠 Intelligence Artificielle (IA) & Bot Professionnel

- **Google Gemini Vision** : Analyse visuelle authentique des photos pour détecter la gravité.
- **Détection Hybride** : Système de double vérification combinant le choix du citoyen et l'expertise de l'IA.
- **Expérience Premium** : Indicateurs de saisie (" typing..."), menu de commandes cliquable, et guide d'utilisation intégré.
- **Commandes Standard** : `/start`, `/help`, `/status`, `/about`, `/privacy`, `/contact`.

### 🗺️ Intelligence Géographique

- **Cartographie interactive** : Localisation précise via geocoding (`geopy`).
- **Carte de chaleur (Heatmap)** : Identification des zones critiques pondérée par la sévérité.

### 🔌 API REST

- **Accès aux données** : Endpoint FastAPI pour récupérer les signalements de fuites.

## 📂 Structure du Projet

```text
WaterAlert/
├── data/               # Base de données SQLite
├── src/
│   ├── api/            # API REST (FastAPI)
│   ├── bot/            # Intelligence du Bot Telegram
│   ├── dashboard/      # Frontend Streamlit & assets CSS
│   ├── database/       # Logique DB (Historique & Tracking)
│   └── utils/          # Utilitaires (IA, Geocoding, PDF)
├── streamlit_app.py    # Point d'entrée principal (Déploiement)
├── verify_setup.py     # Script de diagnostic technique
├── .env                # Configuration (Tokens Telegram & Gemini)
└── requirements.txt    # Dépendances (Streamlit, FastAPI, etc.)
```

## 🛠️ Installation & Configuration

1. **Préparation (Environnement recommandé)** :

   ```powershell
   # Création d'un nouvel environnement si nécessaire
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   *Note : Si vous rencontrez des problèmes avec `venv`, vous pouvez installer les dépendances globalement ou via l'espace utilisateur.*

2. **Variables d'environnement (.env)** :

   Créez un fichier `.env` à la racine (déjà présent et configuré dans votre espace actuel) :

   ```env
   TELEGRAM_BOT_TOKEN=votre_token_botfather
   GEMINI_API_KEY=votre_cle_google_ai_studio
   ```

3. **Vérification du système** :

   Lancez le script de diagnostic pour valider votre installation :

   ```powershell
   python verify_setup.py
   ```

## 🖥️ Utilisation

### Lancer le Bot (Signalement)

```bash
python src/bot/telegram_bot.py
```

### Lancer la Console (Analyse)

```bash
python -m streamlit run streamlit_app.py
```

### Lancer l'API

```bash
python src/api/main.py
```

## 🛡️ Sécurité

- Protection des données sensibles via `.gitignore`.
- Mode "Simulation" automatique si la clé IA est absente.
