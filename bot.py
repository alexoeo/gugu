import discord
import os
from discord import app_commands
from discord.ext import commands
from groq import Groq
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем ключи из файла .env
load_dotenv()

# Ключи теперь берутся из системы, а не из кода
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        await self.tree.sync()
        print("Слэш-команды синхронизированы!")

bot = MyBot()

# --- КОМАНДЫ ---

@bot.tree.command(name="help", description="Список того, что я умею")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Мои возможности", color=discord.Color.blue())
    embed.add_field(name="Модерация", value="/ban, /mute", inline=False)
    embed.add_field(name="Общение", value="Просто тегни меня через @", inline=False)
    embed.add_field(name="Фишки", value="/clear_memory", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Забанить пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Без причины"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member.mention} был забанен.")

@bot.tree.command(name="mute", description="Замутить пользователя")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    duration = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(duration, reason="Нарушение правил")
    await interaction.response.send_message(f"🔇 {member.mention} в муте на {minutes} минут.")

@bot.tree.command(name="clear_memory", description="Очистить историю")
async def clear_memory(interaction: discord.Interaction):
    chat_histories[interaction.channel_id] = []
    await interaction.response.send_message("🧠 Память очищена!")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if bot.user.mentioned_in(message):
        channel_id = message.channel.id
        question = message.content.replace(f'<@!{bot.user.id}>', '').strip()
        if channel_id not in chat_histories: chat_histories[channel_id] = []
        chat_histories[channel_id].append({"role": "user", "content": question})
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "Ты крутой бот-админ."}] + chat_histories[channel_id],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            chat_histories[channel_id].append({"role": "assistant", "content": response})
            await message.reply(response)
        except Exception as e:
            await message.channel.send("Ошибка ИИ.")
            print(e)
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)