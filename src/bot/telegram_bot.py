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
PHOTO, LOCATION = range(2)

db = DBManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bienvenue chez WaterAlert ! 🚰\n"
        "Pour signaler une fuite d'eau, veuillez envoyer une **photo** de la fuite.",
        parse_mode='Markdown'
    )
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    file_path = f"uploads/{user.id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)
    
    context.user_data['photo_path'] = file_path
    
    # Run AI Analysis (Simulated)
    await update.message.reply_text("🔍 *Analyse de l'image par l'IA en cours...*", parse_mode='Markdown')
    is_leak, severity, ai_msg = analyze_leak_image(file_path)
    context.user_data['severity'] = severity
    
    await update.message.reply_text(
        f"{ai_msg}\n\n"
        "Maintenant, veuillez envoyer votre **localisation** (GPS) pour confirmer le signalement.",
        parse_mode='Markdown'
    )
    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_location = update.message.location
    
    photo_path = context.user_data.get('photo_path')
    severity = context.user_data.get('severity', 'Inconnue')
    
    # Get readable address
    await update.message.reply_chat_action("find_location")
    address = get_address(user_location.latitude, user_location.longitude)
    
    db.add_leak(
        user_id=user.id,
        user_name=user.full_name,
        photo_path=photo_path,
        latitude=user_location.latitude,
        longitude=user_location.longitude,
        address=address,
        severity=severity
    )
    
    await update.message.reply_text(
        f"Merci ! Votre signalement à l'adresse suivante a été enregistré :\n📍 *{address}*\n\n"
        "Nos équipes interviendront dès que possible. 🚀",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Signalement annulé.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    leaks = db.get_user_leaks(user.id)
    
    if not leaks:
        await update.message.reply_text("Vous n'avez aucun signalement en cours. Tapez /start pour signaler une fuite !")
        return ConversationHandler.END
        
    response = "*Mes signalements :*\n\n"
    for l in leaks:
        # DB schema: id, user_id, user_name, photo_path, lat, lon, address, severity, technician, status, date
        id_l, _, _, _, _, _, addr, sev, tech, stat, date = l
        response += f"🆔 `#{id_l}` | {stat}\n📍 {addr[:40]}...\n⚠️ Sévérité: {sev}\n"
        if tech:
            response += f"👷 Technicien: {tech}\n"
        response += "---\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')
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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(f"Exception while handling an update: {context.error}")

if __name__ == '__main__':
    if not TOKEN or TOKEN == "YOUR_TOKEN_HERE":
        print("Erreur : Veuillez configurer TELEGRAM_BOT_TOKEN dans le fichier .env")
        exit(1)
        
    # Set increased timeouts for slow networks
    request = HTTPXRequest(connect_timeout=20, read_timeout=20)
    app = ApplicationBuilder().token(TOKEN).request(request).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('status', status)
        ],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            LOCATION: [MessageHandler(filters.LOCATION, location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)
    
    print("Bot is running...")
    app.run_polling()
