import random
import time
import re
import json

import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext

import michel_gruppe
import bot_utils

import db

db.init()
bot = commands.Bot(command_prefix=db.get_command_prefix)
bot_helper = bot_utils.BotUtils(bot)

disconnect_idle_voice_clients = tasks.loop(seconds=10)( # repeat after every 10 seconds
    bot_helper.disconnect_idle_voice_clients
)

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
    sound_file = random.choice(("ok1.ogg", "ok2.ogg"))

    await bot_helper.play_sound_or_give_error(ctx, sound_file)

@bot.command(name="your")
async def botcommand_your(ctx, *args):
    if re.match("^mom'?s a (whore|hoe?)$", " ".join(args)) or True:
        await bot_helper.play_sound_or_give_error(ctx, "your_moms_a_hoe.ogg")

@bot.command(name="i")
async def botcommand_oke(ctx, *args):
    if re.match("^like yo(ur?)? (coochie?|cut g)$", " ".join(args)):
        await bot_helper.play_sound_or_give_error(ctx, "i_like_you_coochie.ogg")


@bot.command(name="say", aliases=["sag","sage"])
async def botcommand_say(ctx, *args):
    sentence = " ".join(args).lower()

    if re.match("^i like yo(ur?)? (coochie?|cut g)$", " ".join(args)):
        await bot_helper.play_sound_or_give_error(ctx, "i_like_you_coochie.ogg")

    elif re.match("^ok$", sentence):
        sound_file = random.choice(("ok1.ogg", "ok2.ogg"))
        await bot_helper.play_sound_or_give_error(ctx, sound_file)

    elif re.match("^oke$", " ".join(args)):
        await bot_helper.play_sound_or_give_error(ctx, "oke.ogg")

    elif re.match("^yo(ur?)? mom'?s a (whore|hoe?)$", " ".join(args)):
        await bot_helper.play_sound_or_give_error(ctx, "your_moms_a_hoe.ogg")


@bot.command(name="leave")
async def botcommand_leave(ctx, *args):
    if ctx.author.voice is None:
        ctx.send("Du bist in keinem Sprachchannel.")
        return

    for voice_client in bot.voice_clients:
        if voice_client.channel == ctx.author.voice.channel:
            await bot_helper.disconnect_voice_client(voice_client)
            break

@bot.command(name="set")
async def botcommand_set(ctx, *args):
    if ctx.message.author.guild_permissions.administrator:
        if len(args) < 2:
            message = "Setze eine Bot-Einstellung im folgenden Format:\n" \
                "```set einstellungsname 'wert'```" \
                "Mögliche Einstellungen sind:\n"
            for setting, value in db.GUILD_SETTINGS.SETTINGS.items():
                message += f"\n - {setting}: \t{db.get_guild_setting(ctx.guild, value)}"

            await ctx.send(message)

        else:
            name = args[0].upper()
            value = args[1]

            if name in db.GUILD_SETTINGS.SETTINGS.keys():
                db.set_guild_setting(
                    ctx.message.guild,
                    db.GUILD_SETTINGS.SETTINGS[name],
                    json.loads(value),
                )
                await ctx.send("Erfolgreich gesetzt")
            else:
                await ctx.send("Einstellung nicht gefunden")
    else:
        await ctx.send("Du hast nicht die nötigen Berechtigungen, um Einstellungen zu setzen")

disconnect_idle_voice_clients.start()
bot.run(TOKEN)

