import asyncio
import os
import time
import interactions
import pymysql
import yt_dlp.utils
from interactions import Extension, ActionRow, Button, ButtonStyle, slash_command, SlashContext, listen
from interactions.api.events import Component
from yt_dlp import YoutubeDL

from concurrent.futures import ThreadPoolExecutor

from modules import MusicQueue, MusicQueueManager
from modules import VideoData
from modules import YTDownloader
from embed import embed_make_pp

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
        "dump_single_json": True,
        "skip_download": True
    }
)
cfg_playlist = YoutubeDL(
    {
        "format": "bestaudio/best",
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
        "extract_flat": True,
        "dump_single_json": True,
        "skip_download": True
    }
)


def get_music_queue(ctx) -> MusicQueue:
    voicestate = ctx.voice_state.channel.voice_state
    server_id = ctx.guild.id
    current_queue = MusicQueueManager.get_queue(server_id, voicestate)
    return current_queue


# Tạo embed playlist


class Music(Extension):
    db_host = "localhost"
    db_user = "root"
    db_pass = os.getenv("db_password")
    VideoData = VideoData()

    def __init__(self, bot):
        self.bot = bot
        print(">> Lệnh Play đã sẵn sàng")

    hang1 = ActionRow(
        Button(custom_id="pause_button", style=ButtonStyle.BLUE, label="⏸️ Tạm Dừng", ),
        Button(custom_id="stop_button", style=ButtonStyle.RED, label="🛑 Dừng ", ),
        Button(custom_id="resume_button", style=ButtonStyle.GREEN, label="▶️ Tiếp tục", ),
        Button(custom_id="loop_button", style=ButtonStyle.GREEN, label="🔂 Lặp lại", ))
    hang2 = ActionRow(
        Button(custom_id="vol_up", style=ButtonStyle.GREEN, label="➕ Tăng Âm Lượng", ),
        Button(custom_id="vol_down", style=ButtonStyle.GREEN, label="➖ Giảm Âm Lượng", ),
        Button(custom_id="skip_button", style=ButtonStyle.GREY, label="⏭️ Tiếp theo", ))

    # lấy ảnh đại diện của người đăng "Video"
    def get_uploader_avatar(self, audio_d):
        url_video = f'https://www.youtube.com/watch?v={audio_d.entry["id"]}'
        return self.VideoData.get_uploader_avt(url_video)

    # Lấy Lớp hàng đợi của server thuộc ctx.guild.id

    @slash_command(name="play", description="Phát bài hát ")
    @interactions.slash_option("song", "Đường dẫn danh sách hoặc video & Tên bài hát", 3, True)
    async def play(self, ctx: SlashContext, song: str):
        await ctx.defer()
        start = time.time()
        """-------------------------------------------------------------------------------"""
        # Thực hiện chuẩn hóa kết nối | Nghĩa là bot có thể tham gia được kênh thoại hiện tại
        if ctx.author.voice is None:
            await ctx.send('Bạn phải ở trong 1 kênh thoại', ephemeral=True)
            return
        else:
            await ctx.author.voice.channel.connect()
        music_queues = get_music_queue(ctx)
        """-------------------------------------------------------------------------------"""
        # Nếu Người dùng ctx Hiện tại đang kết nối với kênh thoại | nghĩa là có thể chuẩn hóa
        if "https://www.youtube.com/playlist?list=" not in song:
            # Đầu vào là một type thuộc Video
            audio = await YTDownloader.get_audio(song)
            avatar_url = self.get_uploader_avatar(audio)
            music_queues.put(audio, avatar_url)
            embed = music_queues.__song_list__[0][0]
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
                # Nếu bot đang chơi nhạc | Chuẩn hóa Embed
                embed.set_author('➕ Đã Thêm Vào hàng đợi')
                await ctx.send(embed=embed)
            else:
                # Nếu Bot đang sẵn sàng
                embed.set_author('📀 Đang Chơi Nhạc')
                await ctx.send(embeds=embed, components=[self.hang1, self.hang2], )
        elif "https://www.youtube.com/playlist?list=" in song:
            # Nếu đầu vào là một playlist
            try:
                start1 = time.time()
                data = await asyncio.to_thread(
                    lambda: cfg_playlist.extract_info(song, download=False)
                )

                def _get_song_info(url: str):
                    try:
                        return cfg_video.extract_info(url, download=False)
                    except yt_dlp.utils.DownloadError:
                        return None

                with ThreadPoolExecutor(max_workers=6) as executor:
                    data_music = executor.map(lambda urld: _get_song_info(urld["url"]),
                                              data["entries"])
                end1 = time.time()
                print('>>>>>>>>> chay lay ppl', end1 - start1)
            except yt_dlp.utils.DownloadError:
                await ctx.send("Danh sách phát không tồn tại", ephemeral=True)
                return

            def _init_music_to_queue(items):
                if items is None:
                    return
                audio_d = YTDownloader.create_new_cls(items)
                avatar_url_d = self.VideoData.get_uploader_avt(direct_url=items)
                music_queues.put(audio_d, avatar_url_d)

            with ThreadPoolExecutor(max_workers=8) as executor:
                executor.map(lambda items: _init_music_to_queue(items), data_music)
            embed = embed_make_pp(data["title"], data["thumbnails"][3]["url"], data["uploader"],
                                  data["playlist_count"])
            if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
                embed.set_author('📀 Đang Chơi')
            await ctx.send(embeds=embed)
            await ctx.send(components=[self.hang1, self.hang2])

        """-------------------------------------------------------------------------------"""
        # Khởi đồng luồng chung | not nếu trường hợp bot không sẵn sàng > Bận nhạc
        if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is False:
            print("đã khởi động luồng")
            self.vol_refresh(ctx)
            end = time.time()
            print('>>>>>>>>>', end - start)
            music_queues.start()

    @slash_command(name="menu", description="Menu chơi nhạc")
    async def _menu(self, ctx: SlashContext):
        await ctx.send(components=[self.hang1, self.hang2])

    @slash_command(name="skip", description="Bỏ qua nhạc")
    async def _skip(self, ctx: SlashContext):
        music_player = get_music_queue(ctx)
        if music_player.peek() is not None:
            await music_player.stop()
            await ctx.send('Đã skip', ephemeral=True)
        else:
            await ctx.send("Hết nhạc trong hàng đợi", ephemeral=True)

    @slash_command(name="stop", description="Dừng Nhạc")
    async def _stop(self, ctx):
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send("Đang không phát nhạc", ephemeral=True)
        else:
            player = ctx.bot.get_bot_voice_state(ctx.guild_id)
            await player.stop()
            await ctx.send('Đã Dừng', ephemeral=True)

    @slash_command(name="resume", description="Tiếp tục nhạc")
    async def _resume(self, ctx):
        music_player = get_music_queue(ctx)
        await music_player.resume()
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send('Đã tiếp tục', ephemeral=True)
        else:
            await ctx.send('Không có nhạc đang dừng', ephemeral=True)

    @slash_command(name="pause", description="tạm dừng nhạc")
    async def _pause(self, ctx):
        music_player = get_music_queue(ctx)
        if ctx.voice_state.channel.voice_state.playing is not True:
            await ctx.send("Đang không phát nhạc")
        else:
            await music_player.pause()
            await ctx.send('Đã tạm dừng', ephemeral=True)

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
                await ctx.send('Đã Tăng âm lượng', ephemeral=True)

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
                await ctx.send('Đã Giảm âm lượng', ephemeral=True)

    # Đặt lại đầu vào âm lượng đã lưu trước đó | Database
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
