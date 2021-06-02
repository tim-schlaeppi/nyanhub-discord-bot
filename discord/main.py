import random
import time
import re
import json
import logging

import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext

import michel_gruppe
import bot_utils
import sound_effects

import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord")
file_handler = logging.FileHandler(filename="discord.log", encoding="UTF8")
logger.addHandler(file_handler)

db.init()

bot = commands.Bot(command_prefix=db.get_command_prefix)
bot_helper = bot_utils.BotUtils(bot)
sound_helper = sound_effects.SoundEffectHelper()


disconnect_idle_voice_clients = tasks.loop(seconds=10)( # repeat after every 10 seconds
    bot_helper.disconnect_idle_voice_clients
)

with open("discord/token.txt") as file:
    TOKEN = file.readline()

@bot.event
async def on_ready():
    print("Bot auf folgenden Servern:")
    for guild in bot.guilds:
        print(f"  {guild.name} (id: {guild.id}, prefix: {db.get_guild_setting(guild.id, 'command_prefix')})")

    print("\nUp and running...")

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    for pagination in bot_helper.paginations:
        if pagination.message == reaction.message:
            if reaction.emoji == bot_utils.Emojis.ARROW_FIRST:
                await pagination.set_page(0)
            elif reaction.emoji == bot_utils.Emojis.ARROW_BACK:
                await pagination.set_page(max(0, pagination.index - 1))
            elif reaction.emoji == bot_utils.Emojis.ARROW_FORWARD:
                await pagination.set_page(min(len(pagination.pages) - 1, pagination.index + 1))
            elif reaction.emoji == bot_utils.Emojis.ARROW_LAST:
                await pagination.set_page(len(pagination.pages) - 1)

            await reaction.remove(user)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "oopsie woopsie":
        logger.info("Oopsie woopsie-Befehl von % erhalten", f"{message.author.name}#{message.author.discriminator}")
        await message.channel.send(file=discord.File(open("img/oopsie_woopise.jpg", "rb"), "oopsie_woopise.jpg"))
        return

    if message.guild and (message.guild.id == michel_gruppe.GUILD_ID):
        logger.debug("Befehl für Modul Michel-Gruppe erhalten: %", message.content)
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


@bot.command(name="ok")
async def botcommand_ok(ctx, *args):
    sound_file = random.choice(("ok1.ogg", "ok2.ogg"))

    await bot_helper.play_sound(ctx, sound_file)


@bot.command(name="your")
async def botcommand_your(ctx, *args):
    if re.match("^mom'?s a (whore|hoe?)$", " ".join(args)) or True:
        await bot_helper.play_sound(ctx, "your_moms_a_hoe.ogg")


@bot.command(name="i")
async def botcommand_oke(ctx, *args):
    if re.match("^like yo(ur?)? (coochie?|cut g)$", " ".join(args)):
        await bot_helper.play_sound(ctx, "i_like_you_coochie.ogg")


@bot.command(name="say", aliases=["sag","sage", "säg"])
async def botcommand_say(ctx, *args):
    sentence = " ".join(args).lower()

    effects = sound_helper.get_effects()

    if re.match("wh[au]t", args[0]):
        entries_per_page = 12

        amount_of_pages = len(effects) // entries_per_page + 1
        pages = ["error 404"]*amount_of_pages
        for i in range(amount_of_pages):
            message = ""
            for effect in effects[i*entries_per_page:min((i+1)*entries_per_page, len(effects))]:
                message += f" - {effect.text} ({effect.abkuerzung})\n"

            pages[i] = message


        await bot_helper.paginate(ctx.message.channel, pages, "Verfügbare Sounds")
        return

    for effect in effects:
        if re.match(effect.regex, sentence) or sentence == effect.abkuerzung:
            await bot_helper.play_sound(ctx, effect.filename)


@bot.command(name="leave")
async def botcommand_leave(ctx, *args):
    if ctx.author.voice is None:
        await ctx.send("Du bist in keinem Sprachchannel.")
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

