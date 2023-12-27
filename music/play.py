import os
import time
from concurrent.futures import ThreadPoolExecutor
import pymysql

import interactions
from interactions import ButtonStyle, ActionRow, Button
from interactions import SlashContext, listen, slash_command

from interactions.api.events import Component
from yt_dlp import YoutubeDL

from embed import embed_make_pp
from modules import MusicQueue, GuildMusicManager
from modules import VideoData
from modules import YTDownloader

cfg_video = YoutubeDL(
    {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        "dump_single_json": True
    }
)

GM = GuildMusicManager()


def get_music_queue(ctx) -> MusicQueue:
    voicestate = ctx.voice_state.channel.voice_state
    server_id = ctx.guild.id
    current_queue = GM.get_queue(server_id, voicestate)
    return current_queue


def get_music_dl(ctx) -> YTDownloader:
    server_id = ctx.guild.id
    currrent_music = GM.get_dl(server_id)
    return currrent_music


class Music(interactions.Extension):
    db_host = "localhost"
    db_user = "root"
    db_pass = os.getenv("db_password")
    VideoData = VideoData()

    def __init__(self, bot):
        self.bot = bot
        print(">> PLay command is ready")

    hang1 = ActionRow(
        Button(custom_id="pause_button", style=ButtonStyle.BLUE, label="⏸️ Pause", ),
        Button(custom_id="stop_button", style=ButtonStyle.RED, label="🛑 Stop", ),
        Button(custom_id="resume_button", style=ButtonStyle.GREEN, label="▶️ resume", ),
        Button(custom_id="loop_button", style=ButtonStyle.GREEN, label="🔂 Loop", ))
    hang2 = ActionRow(
        Button(custom_id="vol_up", style=ButtonStyle.GREEN, label="➕ Vol Up", ),
        Button(custom_id="vol_down", style=ButtonStyle.GREEN, label="➖ Vol down", ),
        Button(custom_id="skip_button", style=ButtonStyle.GREY, label="⏭️ Skip", ))

    def get_uploader_avatar(self, audio_d):
        url_video = f'https://www.youtube.com/watch?v={audio_d.entry["id"]}'
        return self.VideoData.get_uploader_avt(url_video)

    @slash_command(name="play", description="play an music")
    @interactions.slash_option("song", "Playlist link or video tile, link", 3, True)
    async def play(self, ctx: SlashContext, song: str):
        await ctx.defer()
        start = time.time()
        """-------------------------------------------------------------------------------"""

        if ctx.author.voice is None:
            await ctx.send('You must in an voice channel', ephemeral=True)
            return
        else:
            await ctx.author.voice.channel.connect()
        music_queues = get_music_queue(ctx)
        youtube_dl = get_music_dl(ctx)
        """-------------------------------------------------------------------------------"""

        if "https://www.youtube.com/playlist?list=" not in song:

            audio = await youtube_dl.get_audio(song)
            avatar_url = self.get_uploader_avatar(audio)
            music_queues.put(audio, avatar_url)
            embed = music_queues.__song_list__[0][0]
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True or ctx.voice_state.channel.voice_state.paused is True:

                embed.set_author('➕ Added music to queue')
                await ctx.send(embed=embed)
            else:

                embed.set_author('📀 Playing')
                await ctx.send(embeds=embed, components=[self.hang1, self.hang2])
        elif "https://www.youtube.com/playlist?list=" in song:

            data_music = await youtube_dl.ppl_get(song)

            def _init_music_to_queue(items):
                if items is None:
                    return
                avatar_url_d = self.VideoData.get_uploader_avt(direct_url=items)
                audio_d = youtube_dl.create_new_cls(items)
                music_queues.put(audio_d, avatar_url_d)

            with ThreadPoolExecutor(max_workers=8) as executor:
                executor.map(lambda items: _init_music_to_queue(items), data_music[0])
            embed = embed_make_pp(data_music[1]["title"], data_music[1]["thumbnails"][3]["url"],
                                  data_music[1]["uploader"],
                                  data_music[1]["playlist_count"])
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
                embed.set_author('📀 Playing')
            await ctx.send(embeds=embed)
            await ctx.send(components=[self.hang1, self.hang2])

        """-------------------------------------------------------------------------------"""

        if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is False:
            print("already start thread")
            self.vol_refresh(ctx)
            end = time.time()
            print('>>>>>>>>>', end - start)
            music_queues.start()

    @slash_command(name="menu", description="Music Menu")
    async def _menu(self, ctx: SlashContext):
        await ctx.send(components=[self.hang1, self.hang2])

    @slash_command(name="skip", description="Music Skip")
    async def _skip(self, ctx: SlashContext):
        music_player = get_music_queue(ctx)
        if music_player.peek() is not None:
            await music_player.stop()
            await ctx.send('Skipped', ephemeral=True)
        else:
            await ctx.send("Queue is empty", ephemeral=True)

    @slash_command(name="stop", description="Stop Music")
    async def _stop(self, ctx):
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send("Player is not Playing", ephemeral=True)
        else:
            player = ctx.bot.get_bot_voice_state(ctx.guild_id)
            await player.stop()
            await ctx.send('Stopped', ephemeral=True)

    @slash_command(name="resume", description="Resume Music")
    async def _resume(self, ctx):
        music_player = get_music_queue(ctx)
        await music_player.resume()
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send('resumed', ephemeral=True)
        else:
            await ctx.send('there are no music have paused', ephemeral=True)

    @slash_command(name="pause", description="Pause music")
    async def _pause(self, ctx):
        music_player = get_music_queue(ctx)
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send("Player is not playing")
        else:
            await music_player.pause()
            await ctx.send('Paused', ephemeral=True)

    @listen(Component)
    async def on_component(self, event: Component):
        ctx = event.ctx
        match ctx.custom_id:
            case "pause_button":
                await self._pause(ctx)
            case "stop_button":
                await self._stop(ctx)
            case "resume_button":
                await self._resume(ctx)
            case "vol_up":
                await self._volup(ctx)
            case "vol_down":
                await self._voldown(ctx)
            case "skip_button":
                await self._skip(ctx)
            case "loop_button":
                await self._loop(ctx)

    async def _loop(self, ctx):
        player = get_music_queue(ctx)
        player.loop()

    async def _volup(self, ctx):
        player = ctx.bot.get_bot_voice_state(ctx.guild_id)
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database="discord_guild") as connect_thread:
            try:
                with connect_thread.cursor() as cursor:
                    select_query = f"SELECT current_vol FROM server_data WHERE ten_server = '{ctx.guild_id}'"
                    cursor.execute(select_query)
                    result = cursor.fetchone()
                    curr = result[0]
                    curr += 0.15
                    player.volume = curr
                    update_query = f"UPDATE server_data SET current_Vol = %s WHERE ten_server = %s"
                    cursor.execute(update_query, (curr, ctx.guild_id))
                    connect_thread.commit()
            finally:
                await ctx.send('Volume is now inc', ephemeral=True)

    async def _voldown(self, ctx):
        player = ctx.bot.get_bot_voice_state(ctx.guild_id)
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database="discord_guild") as connect_thread:
            try:
                with connect_thread.cursor() as cursor:
                    select_query = f"SELECT current_vol FROM server_data WHERE ten_server = '{ctx.guild_id}'"
                    cursor.execute(select_query)
                    result = cursor.fetchone()
                    curr = result[0]
                    curr -= 0.15
                    player.volume = curr
                    update_query = f"UPDATE server_data SET current_Vol = '{curr}' WHERE ten_server = '{ctx.guild_id}'"
                    cursor.execute(update_query)
                    connect_thread.commit()
            finally:
                await ctx.send('Volume is now dec', ephemeral=True)

    def vol_refresh(self, ctx):
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database="discord_guild") as connect_thread:
            player = ctx.bot.get_bot_voice_state(ctx.guild_id)
            with connect_thread.cursor() as cursor:
                select_query = f"SELECT current_vol FROM server_data WHERE ten_server = '{ctx.guild_id}'"
                cursor.execute(select_query)
                result = cursor.fetchone()
                curr = result[0]
                player.volume = curr
