import random

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

import db

db.init()
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


    if bot.user in message.mentions and "prefix" in message.content:
        prefix = db.get_guild_setting(message.guild, db.GUILD_SETTINGS.COMMAND_PREFIX)
        await message.channel.send(f"Präfix ist '{prefix}'")

    await bot.process_commands(message)

@bot.command(name="prefix")
async def botcommand_prefix(ctx, *args):
    if len(args) > 0:
        db.set_guild_setting(ctx.guild, db.GUILD_SETTINGS.COMMAND_PREFIX, args[0])
        await ctx.send(f"Präfix ist neu '{args[0]}'")

    else:
        prefix = db.get_guild_setting(ctx.guild, db.GUILD_SETTINGS.COMMAND_PREFIX)
        await ctx.send(f"Präfix ist '{prefix}'")

@bot.command(name="hallowelt")
async def botcommand_hallowelt(ctx, *args):
    await ctx.send("Hallo zurück!")

bot.run(TOKEN)

