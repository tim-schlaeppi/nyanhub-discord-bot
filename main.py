import random

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

import db


bot = commands.Bot(command_prefix=db.get_command_prefix)

with open("token.txt") as file:
    TOKEN = file.readline()

@bot.event
async def on_ready():
    print("Bot auf folgenden Servern:")
    for guild in bot.guilds:
        print(f"  {guild.name} (id: {guild.id})")

    print("\nUp and running...")

@bot.event
async def on_message(message):
    if(message.author == bot.user):
        return

    if "69" in message.content:
        await message.channel.send("Nice.")

    if "420" in message.content:
        await message.channel.send("Blaze it")

    if "csgo" in message.content\
            and random.randint(1,20) > 19:
        await message.add_reaction(":csgo:769618730383573062")

    await bot.process_commands(message)

bot.run(TOKEN)

