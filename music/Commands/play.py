import os

import interactions
import pymysql
from interactions import ButtonStyle, ActionRow, Button
from interactions import Embed
from interactions import SlashContext, listen, slash_command
from interactions.api.events import Component
from interactions.ext.paginators import Paginator
from yt_dlp import YoutubeDL

from modules import embed_make_pp
from modules import MusicQueue, GuildMusicManager

GM = GuildMusicManager()

cfg_playlist = YoutubeDL(
    {
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": False,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        # "extract_flat": True,
        # 'dumpjson': True,
        "dump_single_json": True,
        "skip_download": True
    }
)


def get_music_queue(ctx) -> MusicQueue:
    voicestate = ctx.voice_state.channel.voice_state
    server_id = ctx.guild.id
    current_queue = GM.get_queue(server_id, voicestate)
    return current_queue


class Music(interactions.Extension):
    db_host = "localhost"
    db_user = "root"
    db_pass = os.getenv("db_password")

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

    @slash_command(name="play", description="play an music")
    @interactions.slash_option("song", "Playlist link or video tile, link", 3, True)
    async def play(self, ctx: SlashContext, song: str):
        await ctx.defer()
        """-------------------------------------------------------------------------------"""
        if ctx.author.voice is None:
            await ctx.send('You must in an voice channel', ephemeral=True)
            return
        else:
            await ctx.author.voice.channel.connect()
        music_queues = get_music_queue(ctx)
        if ctx.voice_state.channel.voice_state.paused is False:
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is False:
                self.vol_refresh(ctx)
                music_queues.start()
        music_queues.destroy_queue = False
        """-------------------------------------------------------------------------------"""
        if "https://www.youtube.com/playlist?list=" not in song:
            await music_queues.data_process(song, False)
            embed = music_queues.__song_list__[len(music_queues.get_list()) - 1][0]
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True or ctx.voice_state.channel.voice_state.paused is True:
                embed.set_author('➕ Added music to queue')
                await ctx.send(embed=embed)
            else:
                embed.set_author('📀 Playing')
                await ctx.send(embeds=embed, components=[self.hang1, self.hang2])
        elif "https://www.youtube.com/playlist?list=" in song:
            data = cfg_playlist.extract_info(song)
            url_list = list()
            for items in data['entries']:
                url_list.insert(0, f"https://www.youtube.com/watch?v={items['id']}")
            embed = embed_make_pp(data["title"], data["thumbnails"][3]["url"],
                                  data["uploader"],
                                  data["playlist_count"])
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is not True:
                embed.set_author('📀 Playing')
            else:
                embed.set_author('➕ Added music to queue')
            await ctx.send(embeds=embed)
            await ctx.send(components=[self.hang1, self.hang2])
            await music_queues.data_process(url_list, True)
        """-------------------------------------------------------------------------------"""

    @slash_command(name="menu", description="Music Menu")
    async def _menu(self, ctx: SlashContext):
        await ctx.send(components=[self.hang1, self.hang2])

    @slash_command(name="skip", description="Music Skip")
    async def _skip(self, ctx: SlashContext):
        music_player = get_music_queue(ctx)
        if music_player.peek() is not None:
            player = ctx.bot.get_bot_voice_state(ctx.guild_id)
            await player.stop()
            await ctx.send('Skipped', ephemeral=True)
        else:
            await ctx.send("Queue is empty", ephemeral=True)

    @slash_command(name="skipto", description="Play Music at index")
    @interactions.slash_option("index", "index", 4, True)
    async def _skipto(self, ctx: SlashContext, index: int):
        music_player = get_music_queue(ctx)
        print("index: ", index)
        if index > len(music_player.get_list()):
            await ctx.send("Index is out of range", ephemeral=True)
        else:
            await music_player.skipto(index)
            await ctx.send(f'Skipped to {index}', ephemeral=True)

    @slash_command(name="stop", description="Stop Music")
    async def _stop(self, ctx):
        music = get_music_queue(ctx)
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send("Player is not Playing", ephemeral=True)
        else:
            player = ctx.bot.get_bot_voice_state(ctx.guild_id)
            await player.stop()
            await ctx.send('Stopped', ephemeral=True)
            music.clear()

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

    @slash_command(name="view_queue", description="View Music Queue")
    async def _viewplaylist(self, ctx: SlashContext):
        music_player = get_music_queue(ctx)
        data = music_player.get_title_list()
        embeds = []
        count = 0
        embed = Embed(
            title="Danh Sách Hàng đợi",
            color=0x5f9afa,
        )
        for item in data:
            count += 1
            embed.add_field(name=str(count) + ".", value=item, inline=True)
            if count % 25 == 0:
                embeds.append(embed)
                embed = Embed(
                    color=0x5f9afa,
                )
        embeds.append(embed)
        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        await paginator.send(ctx)

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
