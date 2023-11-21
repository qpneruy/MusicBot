import asyncio

import interactions
import pymysql
from interactions import Extension, ActionRow, Button, ButtonStyle, slash_command, SlashContext, listen, \
    Embed
from interactions.api.events import Component
from yt_dlp import YoutubeDL

from modules import YTDownloader
from modules import VideoData
from modules import MusicQueue, MusicQueueManager

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
    }
)


# Đặt lại đầu vào âm lượng đã lưu trước đó | Database
def vol_refresh(ctx):
    connect_thread = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    try:
        with connect_thread.cursor() as cursor:
            select_query = f"SELECT current_vol FROM server_data WHERE ten_server = '{ctx.guild_id}'"
            cursor.execute(select_query)
            result = cursor.fetchone()
            curr = result[0]
            player.volume = curr
    finally:
        connect_thread.close()


# Khởi động luồng từ lớp NAffqueue thuộc ctx.guild.id
async def _fplay(ctx: SlashContext):
    music_queues = get_music_queue(ctx)
    music_queues.start()


def get_music_queue(ctx: SlashContext) -> MusicQueue:
    voicestate = ctx.voice_state.channel.voice_state
    server_id = ctx.guild.id
    current_queue = MusicQueueManager.get_queue(server_id, voicestate)
    return current_queue


# Tạo embed playlist
def embed_make_pp(title: str, thumbnails: str, uploader: str, total: int):
    embed = Embed(
        title=f'{title}',
        description="ㅤ",
        color=0x5f9afa,
    )
    embed.set_author("➕ Đã thêm playlist 📋")
    embed.set_image(thumbnails)
    embed.add_field(name="Author: ", value=f'**{uploader}**', inline=True)
    embed.add_field(name="Số lượng: ", value=f'**{total}**', inline=True)
    return embed


async def _volup(ctx):
    # logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >vol_up \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    connect_thread = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
    try:
        with connect_thread.cursor() as cursor:
            select_query = f"SELECT current_vol FROM server_data WHERE ten_server = '{ctx.guild_id}'"
            cursor.execute(select_query)
            result = cursor.fetchone()
            curr = result[0]
            curr += 0.15
            player.volume = curr
            update_query = f"UPDATE server_data SET current_Vol = '{curr}' WHERE ten_server = '{ctx.guild_id}'"
            cursor.execute(update_query)
            connect_thread.commit()
    finally:
        connect_thread.close()
        await ctx.send('Đã Tăng âm lượng', ephemeral=True)


async def _voldown(ctx):
    # logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >vol_down \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    connect_thread = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
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
        connect_thread.close()
        await ctx.send('Đã Giảm âm lượng', ephemeral=True)


class Music(Extension):
    def __init__(self, bot):
        print(">> Lệnh Play đã sẵn sàng")

    hang1 = ActionRow(
        Button(
            custom_id="pause_button",
            style=ButtonStyle.BLUE,
            label="⏸️ Tạm Dừng",
        ),
        Button(
            custom_id="stop_button",
            style=ButtonStyle.RED,
            label="🛑 Dừng ",
        ),
        Button(
            custom_id="resume_button",
            style=ButtonStyle.GREEN,
            label="▶️ Tiếp tục",
        ),
        Button(
            custom_id="loop_button",
            style=ButtonStyle.GREEN,
            label="🔂 Lặp lại",
        )
    )
    hang2 = ActionRow(
        Button(
            custom_id="vol_up",
            style=ButtonStyle.GREEN,
            label="➕ Tăng Âm Lượng",
        ),
        Button(
            custom_id="vol_down",
            style=ButtonStyle.GREEN,
            label="➖ Giảm Âm Lượng",
        ),
        Button(
            custom_id="skip_button",
            style=ButtonStyle.GREY,
            label="⏭️ Tiếp theo",
        )
    )

    videoinfo = VideoData()

    # lấy ảnh đại diện của người đăng "Video"
    def get_avt_audio(self, audio_d):
        url_video = f'https://www.youtube.com/watch?v={audio_d.entry["id"]}'
        return self.videoinfo.get_uploader_avt(url_video)

    # Lấy Lớp hàng đợi của server thuộc ctx.guild.id

    @slash_command(name="play", description="chơi nhạc")
    @interactions.slash_option("song", "Đường dẫn danh sách hoặc video & Tên bài hát", 3, True)
    async def play(self, ctx: SlashContext, song: str):
        User_inVoice = True
        await ctx.defer()
        """-------------------------------------------------------------------------------"""
        # Thực hiện chuẩn hóa kết nối | Nghĩa là bot có thể tham gia được kênh thoại hiện tại
        if not ctx.voice_state:
            await ctx.author.voice.channel.connect()
            if ctx.author.voice is not None:
                await ctx.author.voice.channel.connect()
                User_inVoice = True
            else:
                await ctx.send('Bạn phải ở trong 1 kênh thoại', ephemeral=True)
                # logger.debug(f'User {ctx.user.display_name} is not in voice channel')
                User_inVoice = False
        """-------------------------------------------------------------------------------"""
        if User_inVoice:
            # Nếu Người dùng ctx Hiện tại đang kết nối với kênh thoại | nghĩa là có thể chuẩn hóa
            if "https://www.youtube.com/playlist?list=" in song:
                # Nếu đầu vào là một playlist
                list_url = []
                data = await asyncio.to_thread(
                    lambda: cfg_playlist.extract_info(song, download=False)
                )
                if "entries" in data:
                    for items in data["entries"]:
                        list_url.insert(0, items)
                if not list_url:
                    await ctx.send('Playplist không tồn tại', ephemeral=True)
                else:
                    # Nếu playlist tồn tại | Được định nghĩa là list_url có url
                    music_queues = get_music_queue(ctx)
                    ppl_info = await YTDownloader.ppl_info(direct_data=data)
                    while True:
                        try:
                            link = list_url.pop()
                        except IndexError:
                            break
                        avatar_url = self.videoinfo.get_uploader_avt(direct_url=link)
                        audio = YTDownloader.create_new_cls(link)
                        await music_queues.put(audio, avatar_url)
                    embed = embed_make_pp(ppl_info["title"], ppl_info["thumbnails"], ppl_info["uploader"],
                                          ppl_info["playlist_count"])
                    if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
                        embed.set_author('📀 Đang Chơi')
                    await ctx.send(embeds=embed)
                    await ctx.send(components=[self.hang1, self.hang2])
                    vol_refresh(ctx)
            else:
                # Đầu vào là một type thuộc Video
                if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
                    # Nếu bot đang chơi nhạc | Chuẩn hóa Embed
                    music_queues = get_music_queue(ctx)
                    audio = await YTDownloader.get_audio(song)
                    avatar_url = self.get_avt_audio(audio)
                    await music_queues.put(audio, avatar_url)
                    embed = music_queues.__song_list__[0]
                    embed.set_author('➕ Đã Thêm Vào hàng đợi')
                    await ctx.send(embed=embed)
                else:
                    # Nếu Bot đang sẵn sàng
                    music_queues = get_music_queue(ctx)
                    audio = await YTDownloader.get_audio(song)
                    avatar_url = self.get_avt_audio(audio)
                    await music_queues.put(audio, avatar_url)
                    embed = music_queues.__song_list__[0]
                    embed.set_author('📀 Đang Chơi Nhạc')
                    await ctx.send(embeds=embed, components=[self.hang1, self.hang2], )
                    vol_refresh(ctx)
        """-------------------------------------------------------------------------------"""
        # Khởi đồng luồng chung | not nếu trường hợp bot không sẵn sàng > Bận nhạc
        if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is False:
            await _fplay(ctx)

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
    async def on_component(self, evnet: Component):
        ctx = evnet.ctx
        match ctx.custom_id:
            case "pause_button":
                await self._pause(ctx)
            case "stop_button":
                await self._stop(ctx)
            case "resume_button":
                await self._resume(ctx)
            case "vol_up":
                await _volup(ctx)
            case "vol_down":
                await _voldown(ctx)
            case "skip_button":
                await self._skip(ctx)
