from datetime import datetime, timedelta

import discord

import db


class VoiceClient:
    voice_client = None
    last_action = None

    def __init__(self, voice_client):
        self.voice_client = voice_client
        self.last_action = datetime.now()

    def update(self):
        self.last_action = datetime.now()

    def play(self, filename):
        self.voice_client.play(discord.FFmpegPCMAudio(f"sounds/{filename}"))

class Pagination:
    pages = None
    message = None
    index = 0
    channel = None
    embed = None

    def __init__(self, channel, pages, title):
        self.pages = pages
        self.title = title
        self.channel = channel
        self.index = 0
        self.embed = discord.Embed(title=self.title, description="")

    async def set_page(self, index):
        self.index = index

        self.embed.description = self.pages[index]
        self.embed.title = self.title + f" ({index+1} / {len(self.pages)})"

        if self.message:
            await self.message.edit(embed=self.embed)
        else:
            message = await self.channel.send(embed=self.embed)
            self.message = message

        await self.message.add_reaction(Emojis.ARROW_FIRST)
        await self.message.add_reaction(Emojis.ARROW_BACK)
        await self.message.add_reaction(Emojis.ARROW_FORWARD)
        await self.message.add_reaction(Emojis.ARROW_LAST)

class BotUtils:
    bot = None
    voice_clients = list()
    paginations = list()

    def __init__(self, bot):
        self.bot = bot

    async def find_existing_channel_or_create_new(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Du bist in keinem Sprachchannel.")
            return

        voicechannel = ctx.author.voice.channel
        voice_client = None

        for bot_voice_client in self.voice_clients:
            if bot_voice_client.voice_client.channel == ctx.author.voice.channel:
                voice_client = bot_voice_client.voice_client
        if voice_client is None:
            voice_client = await voicechannel.connect()
            self.voice_clients.append(VoiceClient(voice_client))

        return voice_client

    async def play_sound(self, ctx, filename):
        voice_client = await self.find_existing_channel_or_create_new(ctx)
        if voice_client:
            voice_client.play(discord.FFmpegPCMAudio(f"sounds/{filename}"))

    async def disconnect_idle_voice_clients(self):
        if len(self.voice_clients) == 0:
            return

        now = datetime.now()
        for element in self.voice_clients:
            max_idle_time = db.get_guild_setting(element.voice_client.guild, db.GUILD_SETTINGS.IDLE_TIME)

            if max_idle_time < 1:
                continue

            if element.last_action + timedelta(seconds=int(max_idle_time)) < now:
                await self.disconnect_voice_client(element.voice_client)

    async def disconnect_voice_client(self, voice_client):
        for i, e in enumerate(self.voice_clients):
            if e.voice_client == voice_client:
                await voice_client.disconnect()
                del self.voice_clients[i]
                break

    async def paginate(self, channel, pages, title):
        pagination = Pagination(channel, pages, title)
        await pagination.set_page(0)
        self.paginations.append(pagination)


    def is_paginated_message(self, message):
        for pagination in self.paginations:
            if pagination.message == message:
                return True
        return False

class Emojis:
    ARROW_FIRST = "\u23ee"
    ARROW_BACK = "\u23ea"
    ARROW_FORWARD = "\u23e9"
    ARROW_LAST = "\u23ed"

