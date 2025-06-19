import os
from dotenv import load_dotenv

load_dotenv()  # 🔹 Loads variables from .env

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler
import aiohttp
import asyncio
import uuid
import html

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Helper: safe API get with retries
async def safe_get(url, retries=3):
    for attempt in range(retries):
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    return await response.json()
        except Exception as e:
            print(f"⚠️ Retry {attempt+1}/{retries} failed:", e)
            await asyncio.sleep(2)
    raise Exception("❌ Failed to connect after retries")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("/anime Naruto"), KeyboardButton("/topanime")],
        [KeyboardButton("/character Luffy"), KeyboardButton("/manga One Piece")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Hello! I’m your Anime Bot.\n\nType or click:\n"
        "📺 /anime <title> - Search anime\n"
        "🔥 /topanime - Top 5 popular anime\n"
        "🎬 Trailer (if available)\n"
        "👤 /character <name> - Search character\n"
        "📖 /manga <title> - Search manga",
        reply_markup=reply_markup
    )

# /topanime command
async def topanime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.jikan.moe/v4/top/anime?limit=5"
    try:
        data = await safe_get(url)
        if 'data' in data:
            reply = "🔥 <b>Top 5 Anime:</b>\n\n"
            for anime in data['data']:
                title = html.escape(anime['title'])
                score = anime.get('score', 'N/A')
                link = anime['url']
                reply += f"<b>{title}</b> - ⭐ {score}\n<a href='{link}'>More Info</a>\n\n"
            await update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=True)
        else:
            await update.message.reply_text("❌ Could not fetch top anime.")
    except Exception as e:
        print("❌ Top Anime Error:", e)
        await update.message.reply_text("⚠️ Failed to load top anime.")

# /anime command with trailer button
async def anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Please type the name of the anime.\nUsage: /anime Naruto")
        return

    query = ' '.join(context.args)
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"

    try:
        data = await safe_get(url)
        if 'data' in data and len(data['data']) > 0:
            anime = data['data'][0]
            title = anime['title']
            episodes = anime.get('episodes', 'Unknown')
            score = anime.get('score', 'N/A')
            synopsis = anime.get('synopsis', 'No synopsis available.')[:300] + '...'
            anime_url = anime['url']
            trailer_url = anime.get('trailer', {}).get('url')

            reply = (
                f"📺 <b>{html.escape(title)}</b>\n"
                f"🎬 Episodes: {episodes}\n"
                f"⭐ Score: {score}\n"
                f"📖 {html.escape(synopsis)}"
            )

            buttons = [
                [InlineKeyboardButton("🔗 More Info", url=anime_url)],
                [InlineKeyboardButton("🔍 Search Again", switch_inline_query_current_chat="/anime ")]
            ]
            if trailer_url:
                buttons.insert(1, [InlineKeyboardButton("🎬 Watch Trailer", url=trailer_url)])

            await update.message.reply_text(reply, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text("❌ No anime found with that name.")
    except Exception as e:
        print("❌ Anime API Error:", e)
        await update.message.reply_text("⚠️ Could not connect to the anime API.")

# /character command (restored)
async def character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Please type the name of the character.\nUsage: /character Goku")
        return

    query = ' '.join(context.args)
    url = f"https://api.jikan.moe/v4/characters?q={query}&limit=1"

    try:
        data = await safe_get(url)
        if 'data' in data and len(data['data']) > 0:
            character = data['data'][0]
            name = character['name']
            about = character.get('about', 'No bio available.')[:300] + '...'
            image_url = character['images']['jpg']['image_url']
            character_url = character['url']

            caption = (
                f"👤 <b>{html.escape(name)}</b>\n"
                f"📝 {html.escape(about)}"
            )

            buttons = [
                [InlineKeyboardButton("🔗 More Info", url=character_url)],
                [InlineKeyboardButton("🔍 Search Again", switch_inline_query_current_chat="/character ")]
            ]

            await update.message.reply_photo(photo=image_url, caption=caption, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text("❌ Character not found.")
    except Exception as e:
        print("❌ Character API Error:", e)
        await update.message.reply_text("⚠️ Could not connect to the character API.")

# /manga command (previously defined)
async def manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Please type the name of the manga.\nUsage: /manga One Piece")
        return

    query = ' '.join(context.args)
    url = f"https://api.jikan.moe/v4/manga?q={query}&limit=1"

    try:
        data = await safe_get(url)
        if 'data' in data and len(data['data']) > 0:
            manga = data['data'][0]
            title = manga['title']
            chapters = manga.get('chapters', 'Unknown')
            volumes = manga.get('volumes', 'Unknown')
            score = manga.get('score', 'N/A')
            synopsis = manga.get('synopsis', 'No synopsis available.')[:300] + '...'
            image_url = manga['images']['jpg']['image_url']
            manga_url = manga['url']

            caption = (
                f"📖 <b>{html.escape(title)}</b>\n"
                f"🗂️ Chapters: {chapters} | Volumes: {volumes}\n"
                f"⭐ Score: {score}\n"
                f"📜 {html.escape(synopsis)}"
            )

            buttons = [
                [InlineKeyboardButton("🔗 More Info", url=manga_url)],
                [InlineKeyboardButton("🔍 Search Again", switch_inline_query_current_chat="/manga ")]
            ]

            await update.message.reply_photo(photo=image_url, caption=caption, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text("❌ No manga found with that name.")
    except Exception as e:
        print("❌ Manga API Error:", e)
        await update.message.reply_text("⚠️ Could not connect to the manga API.")

# Inline query handler (presumed existing)
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = []

    if not query:
        return

    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=5"

    try:
        data = await safe_get(url)
        for item in data.get('data', []):
            title = item.get('title', 'Unknown Title')
            score = item.get('score', 'N/A')
            synopsis = item.get('synopsis', 'No synopsis available.')[:200]
            anime_url = item.get('url', '')

            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=title,
                    description=f"⭐ Score: {score}",
                    input_message_content=InputTextMessageContent(
                        f"<b>{html.escape(title)}</b>\n\n⭐ Score: {score}\n📖 {html.escape(synopsis)}...\n🔗 <a href='{anime_url}'>More Info</a>",
                        parse_mode="HTML"
                    )
                )
            )
        await update.inline_query.answer(results, cache_time=1)
    except Exception as e:
        print("❌ Inline Query Error:", e)

# Run bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("anime", anime))
    app.add_handler(CommandHandler("topanime", topanime))
    app.add_handler(CommandHandler("character", character))
    app.add_handler(CommandHandler("manga", manga))
    app.add_handler(InlineQueryHandler(inline_query))

    print("🤖 Bot running...")
    app.run_polling()
