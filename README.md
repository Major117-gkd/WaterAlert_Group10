# WaterAlert 🚰

WaterAlert est une application de signalement des fuites d’eau permettant aux citoyens d’envoyer des informations géolocalisées accompagnées de photos afin de faciliter l’intervention rapide des sociétés de distribution d’eau.

## Structure du Projet

```
WaterAlert/
├── data/               # Base de données SQLite
├── uploads/            # Photos envoyées par les utilisateurs
├── src/
│   ├── database/       # Logique DB (db_manager.py)
│   ├── bot/            # Bot Telegram (telegram_bot.py)
│   └── dashboard/      # Interface Streamlit (app.py)
├── .env                # Variables d'environnement (Token Bot)
└── requirements.txt    # Dépendances Python
```

## Installation

1.  **Environnement virtuel :**
    - **PowerShell :**
      ```powershell
      python -m venv venv
      .\venv\Scripts\Activate.ps1
      ```
    - **CMD (Invite de commande) :**
      ```cmd
      python -m venv venv
      .\venv\Scripts\activate.bat
      ```

2.  **Dépendances (après activation) :**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration :**
    - Créez un bot via [@BotFather](https://t.me/botfather) sur Telegram.
    - Copiez le token dans le fichier `.env` : `TELEGRAM_BOT_TOKEN=VOTRE_TOKEN`.

## Utilisation

### 1. Lancer le Bot Telegram
```bash
python src/bot/telegram_bot.py
```
Le bot permettra aux citoyens d'envoyer une photo et leur position GPS.

### 2. Lancer le Tableau de Bord Admin
```bash
streamlit run src/dashboard/app.py
```
L'administrateur peut visualiser les signalements sur une carte et mettre à jour leur statut (`Signalé`, `En cours`, `Réparé`).
# WaterAlert_Groupe10
