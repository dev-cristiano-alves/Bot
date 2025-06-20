from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import asyncio

ADMIN_USERNAME = "@crixtianoadm"  # ou ID numérico
ADMIN_ID = 6750676789   # ou ID numérico

# Dicionário para controlar timers por usuário
timers = {}

async def reset_timers(user_id, context: ContextTypes.DEFAULT_TYPE):
    # Cancela timers antigos
    if user_id in timers:
        for task in timers[user_id]:
            task.cancel()
    timers[user_id] = []

    # Agenda mensagem de "você ainda está aí?" em 5 minutos
    task1 = asyncio.create_task(send_check_alive(user_id, context))
    timers[user_id].append(task1)

async def send_check_alive(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        await asyncio.sleep(5 * 60)  # 5 minutos
        await context.bot.send_message(chat_id=user_id, text="👀 Você ainda está aí?")

        # Agenda encerramento em 2 minutos
        task2 = asyncio.create_task(send_end_session(user_id, context))
        timers[user_id].append(task2)

    except asyncio.CancelledError:
        pass

async def send_end_session(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        await asyncio.sleep(2 * 60)  # 2 minutos
        await context.bot.send_message(
            chat_id=user_id,
            text="🛑 Encerrando atendimento por inatividade.\n\n"
                 "Caso queira falar comigo novamente, digite \n/start"
        )
        # Limpa timers após encerramento
        if user_id in timers:
            del timers[user_id]

    except asyncio.CancelledError:
        pass

# Menu Principal (/start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reset_timers(update.effective_user.id, context)

    keyboard = [
        [InlineKeyboardButton("1️⃣ 1 Série", callback_data="1serie")],
        [InlineKeyboardButton("🎬 Combo 5 Séries", callback_data="combo5")],
        [InlineKeyboardButton("💎 Plano VIP", callback_data="vip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(
            "Olá! 👋\nSou o bot atendente do CFLIX.\nGostaria de assistir alguma série? 😍\n\n"
            "Nosso horário de funcionamento é entre às 8h até as 23h\n\n"
            "📚 Veja nosso catálogo completo:\nhttps://t.me/+Mvi_QKiA5XZlN2Qx\n\n"
            "Escolha uma opção abaixo:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Olá! 👋\nSou o bot atendente do CFLIX.\nGostaria de assistir alguma série? 😍\n\n"
            "Nosso horário de funcionamento é entre às 8h até as 23h\n\n"
            "📚 Veja nosso catálogo completo:\nhttps://t.me/+Mvi_QKiA5XZlN2Qx\n\n"
            "Escolha uma opção abaixo:",
            reply_markup=reply_markup
        )

# Voltar ao menu
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update, context)

# Menu Principal - opções
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    await reset_timers(user_id, context)

    query = update.callback_query
    voltar_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data="voltar_menu")]])

    if query.data == "1serie":
        context.user_data["tipo_pagamento"] = "1serie"
        await query.message.reply_text(
            "📌 Após o envio do comprovante de pagamento, você escolhe a série que deseja assistir e será enviado o envio o link.\n\n"
            "💰 Formas de Pagamento:\n"
            "🔹 Pix: ca1pb@outlook.com\n"
            "🔹 PayPal: cristianovieira298@gmail.com\n"
            "🔹 Cartão: [Pagar Agora - $10,00](https://pay.infinitepay.io/crixtiano/VC1D-2PBrR2klVD-10,00)\n"
            "🔹 IBAN: BE24 9051 9386 7338\n\n"
            "📎 Envie o comprovante (imagem ou PDF).\n"
            "⏳ Aguarde um momento até a confirmação do pagamento...",
            reply_markup=voltar_markup
        )

    elif query.data == "combo5":
        context.user_data["tipo_pagamento"] = "combo5"
        await query.message.reply_text(
            "📌 Após a confirmação do pagamento, você poderá escolher até 5 séries.\n"
            "Você pode usar os créditos aos poucos.\n\n"
            "💰 Formas de Pagamento:\n"
            "🔹 Pix: ca1pb@outlook.com\n"
            "🔹 PayPal: cristianovieira298@gmail.com\n"
            "🔹 Cartão: [Pagar Agora - $30,00](https://pay.infinitepay.io/crixtiano/VC1D-2PBrR2klVD-30,00)\n"
            "🔹 IBAN: BE24 9051 9386 7338\n\n"
            "📎 Envie o comprovante (imagem ou PDF).\n"
            "⏳ Aguarde um momento até a confirmação do pagamento...",
            reply_markup=voltar_markup
        )

    elif query.data == "vip":
        keyboard = [
            [InlineKeyboardButton("📆 VIP Semanal", callback_data="vip_semana")],
            [InlineKeyboardButton("📅 VIP Mensal", callback_data="vip_mes")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="voltar_menu")]
        ]
        await query.message.reply_text(
            "Com o VIP você tem acesso ilimitado às séries + novidades diárias!\n\n"
            "Qual plano VIP deseja?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# VIP Semana/Mês
async def handle_vip_planos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    await reset_timers(user_id, context)

    query = update.callback_query
    voltar_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data="voltar_menu")]])

    if query.data == "vip_semana":
        context.user_data["tipo_pagamento"] = "vip_semana"
        await query.message.reply_text(
            "📆 Plano VIP Semanal (7 dias)\n\n"
            "💰 Formas de Pagamento:\n"
            "🔹 Pix: ca1pb@outlook.com\n"
            "🔹 PayPal: cristianovieira298@gmail.com\n"
            "🔹 Cartão: [Pagar Agora - $30,00](https://pay.infinitepay.io/crixtiano/VC1D-2PBrR2klVD-30,00)\n"
            "🔹 IBAN: BE24 9051 9386 7338\n\n"
            "📎 Envie o comprovante (imagem ou PDF).\n"
            "⏳ Aguarde um momento até a confirmação do pagamento...",
            reply_markup=voltar_markup
        )

    elif query.data == "vip_mes":
        context.user_data["tipo_pagamento"] = "vip_mes"
        await query.message.reply_text(
            "📅 Plano VIP Mensal (30 dias)\n\n"
            "💰 Formas de Pagamento:\n"
            "🔹 Pix: ca1pb@outlook.com\n"
            "🔹 PayPal: cristianovieira298@gmail.com\n"
            "🔹 Cartão: [Pagar Agora - $60,00](https://pay.infinitepay.io/crixtiano/VC1D-2PBrR2klVD-60,00)\n"
            "🔹 IBAN: BE24 9051 9386 7338\n\n"
            "📎 Envie o comprovante (imagem ou PDF).\n"
            "⏳ Aguarde um momento até a confirmação do pagamento...",
            reply_markup=voltar_markup
        )

# Envio de comprovante
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    await reset_timers(user_id, context)

    tipo = context.user_data.get("tipo_pagamento", "desconhecido")

    await update.message.reply_text("✅ Comprovante recebido! Enviando para o administrador para verificação...")

    texto_adm = (
        f"📩 Novo pagamento de @{user.username or user.first_name} (ID: {user.id})\n"
        f"🧾 Tipo: {tipo.replace('_', ' ').upper()}\n\n"
        f"Você recebeu o pagamento?\n"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Sim", callback_data=f"confirmado_{user.id}")],
        [InlineKeyboardButton("❌ Não", callback_data=f"recusado_{user.id}")]
    ]
    await context.bot.send_message(chat_id=ADMIN_ID, text=texto_adm, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Confirmação ADM
async def resposta_adm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    await reset_timers(user_id, context)

    data = query.data

    if data.startswith("confirmado_"):
        user_id_to_send = int(data.split("_")[1])
        tipo = context.user_data.get("tipo_pagamento", "")
        if "vip" in tipo:
            await context.bot.send_message(
                chat_id=user_id_to_send,
                text=(
                    "✅ Pagamento confirmado!\n\n"
                    "🔗 Acesse o grupo VIP:\nhttps://t.me/+JWoPsvndViY0MmVh\n\n"
                    f"⚠️ Após pedir para entrar, avise o suporte: {ADMIN_USERNAME}"
                )
            )
        else:
            await context.bot.send_message(
                chat_id=user_id_to_send,
                text=(
                        f"✅ Pagamento confirmado! MUITO OBRIGADO POR SUA COMPRA.\n\n Agora Por favor, envie o nome da(s) série(s) para o suporte: {ADMIN_USERNAME}\n\n"
                        f"Para falar comigo novamente digite /start"
                        )
            )

    elif data.startswith("recusado_"):
        user_id_to_send = int(data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id_to_send,
            text=(
                    f"❌ Pagamento não confirmado. Tente novamente ou fale com nosso suporte: {ADMIN_USERNAME}\n\n"
                    f"Para falar comigo novamente digite /start"
                    )        
        )

# Resetar timers em mensagens normais (não comandos)
async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await reset_timers(user_id, context)
    # Pode responder ou não, dependendo da lógica do seu bot
    # Exemplo:
    # await update.message.reply_text("Recebi sua mensagem!")

# Resetar timers em callback queries
async def handle_any_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await reset_timers(user_id, context)
    await update.callback_query.answer()

# MAIN
if __name__ == '__main__':
    app = ApplicationBuilder().token("7719732942:AAFlrJ3lOCHpASjI6eOprPe2XvNtTR6D2gw").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_callback, pattern="^voltar_menu$"))
    app.add_handler(CallbackQueryHandler(handle_menu, pattern="^(1serie|combo5|vip)$"))
    app.add_handler(CallbackQueryHandler(handle_vip_planos, pattern="^vip_"))
    app.add_handler(CallbackQueryHandler(resposta_adm, pattern="^(confirmado_|recusado_).*"))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

    # Handlers para resetar o timer de inatividade
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_any_message))
    app.add_handler(CallbackQueryHandler(handle_any_callback))

    print("🤖 Bot CFLIX rodando...")
    app.run_polling()
