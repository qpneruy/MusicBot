import discord
import os
from discord.ext import commands
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
token = os.getenv("Discord_Token_bot_B")
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'>>Bot đã hoạt động! tên: {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    channels = bot.get_channel('1158628441193725982')
    if before.channel is not None and before.channel == channels:
        print(before.channel)
        new_channel = await move_to_new_channel(member)
        await member.move_to(new_channel)
    elif after.channel is None:
        await delete_channel(before.channel)

async def move_to_new_channel(member):
    guild = member.guild
    new_channel = await guild.create_voice_channel(member.name)
    return new_channel

async def delete_channel(channel):
    await channel.delete()

bot.run(token)