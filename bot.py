import json
import time
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
OWNERS = {8638978228}
ADMINS = set()
warnings_db = {}

def is_admin(user_id):
    return user_id in OWNERS or user_id in ADMINS

def is_owner(user_id):
    return user_id in OWNERS
async def addadmin(update, context):
    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    ADMINS.add(user.id)

    await update.message.reply_text(f"{user.first_name} ahora es admin ⚡")

async def removeadmin(update, context):
    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Responde a un usuario")
        return

    user = update.message.reply_to_message.from_user

    if user.id in ADMINS:
        ADMINS.remove(user.id)
        await update.message.reply_text(f"{user.first_name} ya no es admin ❌")
    else:
        await update.message.reply_text("Ese usuario no es admin")

async def addowner(update, context):
    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Responde a un usuario")
        return

    user = update.message.reply_to_message.from_user
    OWNERS.add(user.id)

    await update.message.reply_text(f"{user.first_name} ahora es owner 👑")

TOKEN = "8957744605:AAHtKylOR4Y3YMpBgxOMWkVUbR07AFP44fI"

DB_FILE = "db.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"owners": [], "groups": {}, "global_bans": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    chat_id = str(update.effective_chat.id)

    group = db["groups"].setdefault(chat_id, {"users": {}})

    for user in update.message.new_chat_members:
        group["users"][str(user.id)] = int(time.time())

    save_db(db)

async def setowner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()

    if not db["owners"]:
        db["owners"].append(update.effective_user.id)
        save_db(db)
        return await update.message.reply_text("👑 Eres el owner")

    await update.message.reply_text("Ya existe owner")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("No tienes permiso 🚫")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Responde a un usuario")
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id

    await context.bot.restrict_chat_member(
        chat_id,
        user.id,
        ChatPermissions(can_send_messages=False)
    )

    await update.message.reply_text(f"{user.first_name} fue silenciado 🔇")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        permissions=ChatPermissions(can_send_messages=True)
    )

    await update.message.reply_text("🔊 Activado")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("No tienes permiso 🚫")
        return
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user

    if user.id not in db["global_bans"]:
        db["global_bans"].append(user.id)

    save_db(db)

    for chat_id in db["groups"]:
        try:
            await context.bot.ban_chat_member(int(chat_id), user.id)
        except:
            pass

    await update.message.reply_text("🚫 Baneado global")

async def warn(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("No tienes permiso 🚫")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Responde a un usuario")
        return

    user = update.message.reply_to_message.from_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if user_id not in warnings_db:
        warnings_db[user_id] = 0

    warnings_db[user_id] += 1
    warns = warnings_db[user_id]

    if warns >= 3:
        await context.bot.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )

        warnings_db[user_id] = 0

        await update.message.reply_text(
            f"{user.first_name} fue silenciado 🔇"
        )
    else:
        await update.message.reply_text(
            f"{user.first_name} tiene {warns}/3 advertencias ⚠️"
        )

app = ApplicationBuilder().token("8957744605:AAHtKylOR4Y3YMpBgxOMWkVUbR07AFP44fI").build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, join))
app.add_handler(CommandHandler("setowner", setowner))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("addadmin", addadmin))
app.add_handler(CommandHandler("removeadmin", removeadmin))
app.add_handler(CommandHandler("addowner", addowner))

app.run_polling()



