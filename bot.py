import discord
from discord import app_commands
from discord.ext import commands
from groq import Groq
from datetime import timedelta

# 1. Настройка
GROQ_API_KEY = "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"
DISCORD_TOKEN = "MTUxNzA4MDA5MTg4NzI3NjA0Mw.Gumxlu.kc83_MyNp-IrMTjKB9bKXxOAIRWt5zY1pI0Z4o"

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        # Синхронизируем слэш-команды с Discord
        await self.tree.sync()
        print("Слэш-команды синхронизированы!")

bot = MyBot()

# --- ФИШКИ И МОДЕРАЦИЯ ---

@bot.tree.command(name="help", description="Список того, что я умею")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Мои возможности", color=discord.Color.blue())
    embed.add_field(name="Модерация", value="/ban, /kick, /mute", inline=False)
    embed.add_field(name="Общение", value="Просто тегни меня через @, и я отвечу с памятью контекста!", inline=False)
    embed.add_field(name="Фишки", value="/clear - очистить память, /ping - проверка задержки", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Забанить пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Без причины"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member.mention} был забанен. Причина: {reason}")

@bot.tree.command(name="mute", description="Замутить пользователя (отправить в таймаут)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration, reason="Нарушение правил")
    await interaction.response.send_message(f"🔇 {member.mention} в муте на {minutes} минут.")

@bot.tree.command(name="clear_memory", description="Очистить историю диалога")
async def clear_memory(interaction: discord.Interaction):
    chat_histories[interaction.channel_id] = []
    await interaction.response.send_message("🧠 Память этого чата очищена!")

# --- ОБРАБОТКА ТЕКСТА (с памятью) ---

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
                messages=[{"role": "system", "content": "Ты крутой бот-админ с чувством юмора."}] + chat_histories[channel_id],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            chat_histories[channel_id].append({"role": "assistant", "content": response})
            await message.reply(response)
        except Exception as e:
            await message.channel.send("Ошибка ИИ.")
            print(e)

bot.run(DISCORD_TOKEN)
