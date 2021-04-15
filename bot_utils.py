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


class BotUtils:
    bot = None
    voice_clients = list()

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

    async def play_sound_or_give_error(self, ctx, filename):
        voice_client = await self.find_existing_channel_or_create_new(ctx)
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