"""Telegram channel. Passive unless both the token and the allowed user id are set."""

from __future__ import annotations

import logging
from pathlib import Path

from grasshopper.publish.live import running_screenshot

log = logging.getLogger("grasshopper.telegram")


def telegram_enabled(settings) -> bool:
    return bool(settings.telegram_bot_token and settings.telegram_allowed_user_id)


async def deliver_canli(ctx, user_id: str, *, send_photo, send_text) -> str:
    """Send the running task's latest frame to the allowed user only."""
    allowed = str(ctx.settings.telegram_allowed_user_id or "")
    if not allowed or str(user_id) != allowed:
        return "ignored"
    shot = running_screenshot(ctx)
    if shot is None:
        await send_text("No running task with a screenshot.")
        return "none"
    await send_photo(shot)
    return "photo"


def build_telegram_application(ctx):
    if not telegram_enabled(ctx.settings):
        log.info("Telegram channel is passive")
        return None
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

    allowed = str(ctx.settings.telegram_allowed_user_id)

    def _allowed(update: Update) -> bool:
        user = update.effective_user
        return user is not None and str(user.id) == allowed

    async def on_text(update: Update, context):
        if not _allowed(update) or not update.message:
            return
        task = ctx.orchestrator.accept(update.message.text or "", channel="telegram")
        await update.message.reply_text(f"Queued {task.id}")

    async def on_voice(update: Update, context):
        if not _allowed(update) or not update.message or not update.message.voice:
            return
        folder = ctx.settings.data_dir / "audio"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{update.message.voice.file_id}.ogg"
        telegram_file = await update.message.voice.get_file()
        await telegram_file.download_to_drive(custom_path=str(path))
        text = await ctx.stt.transcribe(str(path))
        task = ctx.orchestrator.accept(text, channel="telegram")
        await update.message.reply_text(f"Heard: {text}\nQueued {task.id}")

    async def on_canli(update: Update, context):
        if not _allowed(update) or update.message is None or update.effective_user is None:
            return

        async def send_photo(path: Path):
            with path.open("rb") as handle:
                await context.bot.send_photo(chat_id=allowed, photo=handle)

        async def send_text(text: str):
            await context.bot.send_message(chat_id=allowed, text=text)

        await deliver_canli(ctx, str(update.effective_user.id), send_photo=send_photo, send_text=send_text)

    async def on_callback(update: Update, context):
        if not _allowed(update) or not update.callback_query:
            return
        data = update.callback_query.data or ""
        action, _, approval_id = data.partition(":")
        if action not in {"approve", "reject"} or not approval_id:
            return
        decision = "approved" if action == "approve" else "rejected"
        ctx.gate.decide(approval_id, decision)
        await update.callback_query.answer(decision)
        await update.callback_query.edit_message_text(f"{decision}: {approval_id}")

    application = Application.builder().token(ctx.settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("canli", on_canli))
    application.add_handler(CommandHandler("start", on_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    application.add_handler(MessageHandler(filters.VOICE, on_voice))
    application.add_handler(CallbackQueryHandler(on_callback))
    application.bot_data["grasshopper"] = ctx
    # Inline keyboards are sent by TelegramNotifier, not this function.
    _ = InlineKeyboardButton, InlineKeyboardMarkup, Path
    return application
