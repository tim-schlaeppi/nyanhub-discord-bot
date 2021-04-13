import random
import time

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

import michel_gruppe

import db

db.init()
bot = commands.Bot(command_prefix=db.get_command_prefix)

with open("token.txt") as file:
    TOKEN = file.readline()

@bot.event
async def on_ready():
    print("Bot auf folgenden Servern:")
    for guild in bot.guilds:
        print(f"  {guild.name} (id: {guild.id}, prefix: {db.get_guild_setting(guild.id, 'command_prefix')})")

    print("\nUp and running...")

@bot.event
async def on_message(message):
    if(message.author == bot.user):
        return

    if message.guild and (message.guild.id == michel_gruppe.GUILD_ID):
        await michel_gruppe.process_message(message)
        return

    if bot.user in message.mentions and "prefix" in message.content:
        prefix = db.get_guild_setting(message.guild, db.GUILD_SETTINGS.COMMAND_PREFIX)
        await message.channel.send(f"Präfix ist '{prefix}'")

        if "prefix:" in message.content:
            if message.author.guild_permissions.administrator:
                new_prefix = message.content.split(":", 1)[1]
                db.set_guild_setting(message.guild, db.GUILD_SETTINGS.COMMAND_PREFIX, new_prefix)
                await message.channel.send(f"Präfix wird auf '{new_prefix}' geändert.")
            else:
                await message.channel.send("Du hast keine Berechtigung, das Präfix zu setzen.")

    if "welcher tim" in message.content.lower() or "welchen tim" in message.content.lower():
        tim = random.choice([
            "Meringü",
            "Dolan Duck",
            "tiLarMANU",
        ])
        await message.channel.send(f"Ich denke es war {tim}")

    if message.content == "ok" and random.randint(0, 5) == 0:
        await message.channel.send("https://media.timschlaeppi.ch/img/ok.png")

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

@bot.command(name="lanes")
async def botcommand_lanes(ctx, *args):
    pass

@bot.command(name="ok")
async def botcommand_ok(ctx, *args):
    if ctx.author.voice is None:
        ctx.send("Du bist in keinem Sprachchannel.")
        return

    voicechannel = ctx.author.voice.channel
    voice_client = None

    for bot_voice_client in bot.voice_clients:
        if bot_voice_client.channel == ctx.author.voice.channel:
            voice_client = bot_voice_client
    if voice_client is None:
        voice_client = await voicechannel.connect()

    sound_file = "sounds/" + random.choice(("ok1.ogg", "ok2.ogg"))

    voice_client.play(discord.FFmpegPCMAudio(sound_file))

@bot.command(name="leave")
async def botcommand_leave(ctx, *args):
    if ctx.author.voice is None:
        ctx.send("Du bist in keinem Sprachchannel.")
        return

    print(bot.voice_clients)

    for voice_client in bot.voice_clients:
        if voice_client.channel == ctx.author.voice.channel:
            await voice_client.disconnect()

bot.run(TOKEN)

