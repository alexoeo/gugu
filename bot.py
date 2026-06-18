import discord
import os
from discord import app_commands
from discord.ext import commands
from groq import Groq
from datetime import timedelta # Исправленный импорт

# Прямое чтение токенов (если не хочешь .env, просто вставь ключи в кавычки)
# Но лучше использовать переменные окружения, как мы договорились
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client = Groq(api_key=GROQ_API_KEY)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Бот в сети и слэш-команды работают!")

@bot.tree.command(name="mute", description="Замутить пользователя")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    duration = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(duration, reason="Нарушение")
    await interaction.response.send_message(f"🔇 {member.mention} в муте на {minutes} минут.")

bot.run(DISCORD_TOKEN)