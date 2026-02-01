import os
import logging
import asyncio
import sys
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Specific fix for Windows asyncio issues with python-telegram-bot/httpx
if sys.platform == 'win32':
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DBManager
from utils.geocoder import get_address
from utils.ai_analyzer import analyze_leak_image

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PHOTO, SEVERITY, LOCATION = range(3)

db = DBManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_chat_action("typing")
    await update.message.reply_text(
        "👋 **Bienvenue sur WaterAlert !**\n\n"
        "Je suis votre assistant intelligent pour la protection de nos ressources en eau. "
        "Ensemble, agissons rapidement contre les fuites.\n\n"
        "📸 Pour commencer, envoyez-moi une **photo** de la fuite.\n\n"
        "💡 _Tapez /help pour voir le guide ou utilisez le Menu en bas à gauche._",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return PHOTO

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_chat_action("typing")
    help_text = (
        "📖 **Guide d'utilisation WaterAlert**\n\n"
        "1️⃣ **Photo** : Envoyez une photo claire de la fuite.\n"
        "2️⃣ **Analyse** : L'IA évalue la gravité en quelques secondes.\n"
        "3️⃣ **Gravité** : Confirmez le niveau de sévérité.\n"
        "4️⃣ **Position** : Partagez votre position GPS.\n\n"
        "📌 **Commandes :**\n"
        "/start - Signaler une fuite\n"
        "/status - État de mes signalements\n"
        "/about - En savoir plus sur le projet\n"
        "/privacy - Protection de vos données\n"
        "/cancel - Annuler"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_chat_action("typing")
    text = (
        "🌍 **À propos de WaterAlert**\n\n"
        "WaterAlert est une initiative citoyenne et technologique visant à réduire le gaspillage d'eau potable. "
        "Grâce à l'Intelligence Artificielle de Google Gemini, nous traitons vos signalements en temps réel "
        "pour prioriser les interventions d'urgence.\n\n"
        "📡 **Technologie** : Python, FastAPI, Streamlit, IA Vision.\n"
        "🤝 **Partenariat** : Collaboration avec les services techniques municipaux."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_chat_action("typing")
    text = (
        "🛡️ **Protection des Données (RGPD)**\n\n"
        "Vos données sont traitées avec le plus grand respect :\n"
        "• **Photos** : Utilisées uniquement pour l'analyse de la fuite.\n"
        "• **Position** : Utilisée exclusivement pour localiser la fuite.\n"
        "• **Identité** : Seul votre nom public Telegram est enregistré.\n\n"
        "Vous pouvez demander la suppression de vos données à tout moment via /contact."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_chat_action("typing")
    text = (
        "✉️ **Contact & Support**\n\n"
        "Une question ? Un problème technique ?\n"
        "Contactez l'équipe WaterAlert :\n"
        "📧 Email : `support@wateralert.tech` (exemple)\n"
        "📱 Telegram : @WaterAlertSupport"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{user.id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)
    context.user_data['photo_path'] = file_path
    
    await update.message.reply_chat_action("typing")
    await update.message.reply_text("🔍 *Analyse IA en cours... Merci de patienter.*", parse_mode='Markdown')
    
    is_leak, ai_severity, ai_msg = analyze_leak_image(file_path)
    
    await update.message.reply_chat_action("typing")
    if not is_leak:
        await update.message.reply_text(
            f"{ai_msg}\n\n"
            "⚠️ Désolé, l'IA n'a pas détecté de fuite évidente. Envoyez une **autre photo** ou tapez /cancel.",
            parse_mode='Markdown'
        )
        return PHOTO

    context.user_data['ai_severity'] = ai_severity
    
    reply_keyboard = [
        ["💧 Petite (Goutte à goutte)"],
        ["🌊 Moyenne (Filet d'eau)"],
        ["🆘 Élevée (Geyser / Inondation)"]
    ]
    
    await update.message.reply_text(
        f"{ai_msg}\n\n"
        "Veuillez confirmer la **gravité** observée :",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode='Markdown'
    )
    return SEVERITY

async def severity_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    severity = "Petite" if "Petite" in choice else "Moyenne" if "Moyenne" in choice else "Élevée"
    context.user_data['user_severity'] = severity
    
    await update.message.reply_chat_action("typing")
    await update.message.reply_text(
        "📍 Parfait. Veuillez maintenant envoyer votre **localisation** GPS via l'icône 📎.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_location = update.message.location
    
    photo_path = context.user_data.get('photo_path')
    severity = context.user_data.get('user_severity', 'Inconnue')
    ai_severity = context.user_data.get('ai_severity', 'Inconnue')
    
    await update.message.reply_chat_action("find_location")
    address = get_address(user_location.latitude, user_location.longitude)
    
    db.add_leak(
        user_id=user.id,
        user_name=user.full_name,
        photo_path=photo_path,
        latitude=user_location.latitude,
        longitude=user_location.longitude,
        address=address,
        severity=severity,
        ai_severity=ai_severity
    )
    
    await update.message.reply_chat_action("typing")
    reply_keyboard = [["🆕 Nouveau signalement"], ["📊 Mes signalements"]]
    
    await update.message.reply_text(
        f"✅ **Signalement validé !**\n\n"
        f"📍 Adresse : _{address}_\n"
        "Nos services ont été alertés. Merci pour votre engagement citoyen ! 🚀",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return ConversationHandler.END

async def send_status_notification(user_id, leak_id, new_status):
    """Function to be called from the dashboard to notify users."""
    status_msg = {
        "En cours": "🛠️ Votre signalement #{} est maintenant **en cours d'intervention**.",
        "Réparé": "✅ Bonne nouvelle ! La fuite signalée (#{}) a été **réparée**. Merci de votre aide !"
    }
    msg = status_msg.get(new_status, "ℹ️ Le statut de votre signalement #{} a été mis à jour : **{}**.")
    
    async with ApplicationBuilder().token(TOKEN).build() as app:
        await app.bot.send_message(chat_id=user_id, text=msg.format(leak_id, new_status), parse_mode='Markdown')

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown messages or random text."""
    await update.message.reply_chat_action("typing")
    await update.message.reply_text(
        "🤔 Je n'ai pas bien compris.\n\n"
        "Pour signaler une fuite d'eau, utilisez /start ou le bouton **Menu** en bas à gauche. 🚰",
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_chat_action("typing")
    await update.message.reply_text(
        "Signalement annulé. Vous pouvez recommencer à tout moment.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_chat_action("typing")
    user = update.message.from_user
    leaks = db.get_user_leaks(user.id)
    
    if not leaks:
        await update.message.reply_text("Vous n'avez aucun signalement actif. Utilisez /start pour agir !")
        return ConversationHandler.END
        
    response = "📊 **Vos signalements :**\n\n"
    for l in leaks:
        id_l, _, _, _, _, _, addr, sev, tech, stat, date = l
        response += f"🆔 `#{id_l}` | {stat}\n📍 {addr[:40]}...\n⚠️ {sev}\n---\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return ConversationHandler.END

async def post_init(application) -> None:
    """Setup bot professional profile and menu on startup."""
    from telegram import BotCommand
    commands = [
        BotCommand("start", "Signaler une nouvelle fuite"),
        BotCommand("status", "Voir mes signalements"),
        BotCommand("about", "À propos de WaterAlert"),
        BotCommand("help", "Guide d'utilisation"),
        BotCommand("contact", "Contacter le support"),
        BotCommand("privacy", "Protection des données"),
        BotCommand("cancel", "Annuler l'action")
    ]
    await application.bot.set_my_commands(commands)
    # Set bot description (shown in profile and chat start)
    await application.bot.set_my_description(
        "L'assistant citoyen pour signaler les fuites d'eau en temps réel. "
        "Utilisant l'IA pour sauver nos ressources précieuses."
    )
    await application.bot.set_my_short_description("Signalez les fuites d'eau avec l'IA 🚰")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(f"Exception while handling an update: {context.error}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN_HERE":
        print("Erreur : Veuillez configurer TELEGRAM_BOT_TOKEN dans le fichier .env")
        exit(1)
        
    request = HTTPXRequest(connect_timeout=20, read_timeout=20)
    app = ApplicationBuilder().token(TOKEN).request(request).post_init(post_init).build()

    # Global commands
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('about', about))
    app.add_handler(CommandHandler('privacy', privacy))
    app.add_handler(CommandHandler('contact', contact))
    app.add_handler(MessageHandler(filters.Regex("^📊 Mes signalements$"), status))
    app.add_handler(MessageHandler(filters.Regex("^🆕 Nouveau signalement$"), start))
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("^🆕 Nouveau signalement$"), start),
        ],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            SEVERITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, severity_choice)],
            LOCATION: [MessageHandler(filters.LOCATION, location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), unknown))
    app.add_error_handler(error_handler)
    
    print("Bot is running...")
    app.run_polling()
