import os
import asyncio
import datetime as dt
import interactions
from typing_extensions import Self
import random
from collections import deque
from typing import Iterator
from yt_dlp import YoutubeDL
from interactions import SlashContext, listen, slash_command, Embed, OptionType, slash_option, ActiveVoiceState, \
    ButtonStyle, ActionRow, Button
# from interactions.models.discord.channel import ThreadChannel || phát triển code sử dụng module threadchannel
from interactions.api.events import Startup, VoiceStateUpdate, Component
from interactions.api.voice.audio import AudioVolume, BaseAudio
import logging
import datetime

now = datetime.datetime.now()
formatted_time = now.strftime('%Y-%m-%d_%H-%M')
log_filename = f'log_{formatted_time}.txt'
logger = logging.getLogger('discord_log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_filename, encoding='utf-8')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

Token = os.getenv("Discord_Token_Bot_A")
# Token = os.getenv("Discord_Token_bot_B")
bot = interactions.Client()
startup = dt.datetime.utcnow()
youtube_dl = YoutubeDL(
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
        "source_address": "0.0.0.0",  # noqa: S104
    }
)


class NaffQueue:
    voice_state: ActiveVoiceState
    _entries: deque
    _item_queued: asyncio.Event
    loopstate: bool
    last: BaseAudio

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self._item_queued = asyncio.Event()
        self.__song_list__ = []
        self._current_task = None
        self.loopstate = False

    def __len__(self) -> int:
        return len(self._entries)

    def loops(self) -> None:
        if not self.loopstate:
            self.loopstate = True
        elif self.loopstate:
            self.loopstate = False

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    def put(self, audio_d: BaseAudio) -> None:
        self._entries.append(audio_d)
        self._item_queued.set()

    def get_list(self) -> list:
        return self.__song_list__

    def put_first(self, audio_d: BaseAudio) -> None:
        self._entries.appendleft(audio_d)
        self._item_queued.set()

    async def pop(self) -> BaseAudio:
        if len(self) == 0:
            await self._item_queued.wait()
        item = self._entries.popleft()
        # self._item_queued.clear()
        return item

    def pop_no_wait(self) -> BaseAudio:
        return self._entries.popleft()

    def shuffle(self) -> None:
        random.shuffle(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def peek(self, positions: int = 1) -> BaseAudio | None:
        try:
            return self._entries[positions - 1]
        except IndexError:
            return None

    def peek_at_index(self, index: int) -> BaseAudio:
        return self._entries[index]

    async def __playback_queue(self) -> None:
        while self.voice_state.connected:
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            if not self.loopstate:
                audio = await self.pop()
                embed = self.__song_list__.pop()
                await self.voice_state.channel.send(embed=embed)
                await self.voice_state.channel.send(audio.entry['title'])
            else:
               await self.voice_state.connect(1)
            print(audio)
            if audio is not None:

                await self.voice_state.play(audio)


        # >> code lặp cần fix << >>> put_at_index tránh việc đang lặp mà thêm bài hát vào
        # while self.voice_state.connected:
        #     if self.voice_state.playing:
        #         await self.voice_state.wait_for_stopped()
        #     audio_d = await self.pop()
        #     if audio_d is not None:
        #         embed = self.__song_list__.pop()
        #         await self.voice_state.channel.send(embed=embed)
        #     await self.voice_state.play(audio_d)

    async def _stop(self) -> None:
        await self.voice_state.stop()

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        if self._current_task is not None:
            self._current_task.cancel()
            self._stop()
        self._current_task = asyncio.create_task(self())

    async def skip(self):
        next_audio = await self.pop()
        await self.voice_state.play(next_audio)


class YTAudio(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None

    @classmethod
    async def from_url(
            cls, url: str, stream: bool = True, ytdl: YoutubeDL | None = None) -> Self:
        if not ytdl:
            ytdl = youtube_dl
        data = await asyncio.to_thread(
            lambda: ytdl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            data = data["entries"][0]
        filename = data["url"] if stream else ytdl.prepare_filename(data)
        new_cls = cls(filename)
        if stream:
            new_cls.ffmpeg_before_args = (
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            )
        new_cls.entry = data
        return new_cls


@listen(Startup)
async def _starup():
    logger.debug(f" >> Bot Da Hoat dong! Ten: {bot.user.display_name}")
    await bot.change_presence(status=interactions.Status.IDLE, activity="lệnh /help để giúp đỡ")


@slash_command(name="help", description="Trợ Giúp")
async def _help(ctx: SlashContext):
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} > HELP")
    embed = Embed(
        title="**Giúp Đỡ**                       ",
        description="  ",
        color=0x6DAEDB,
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="**📖️ ╏ COMMAND**", value='ㅤ  /about -- Trạng thái bot\nㅤ /Play -- Chơi nhạc')
    await ctx.send(embed=embed)


@slash_command(name="about", description="Trạng Thái Bot")
async def _about(ctx: SlashContext):
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} > ABOUT")
    embed2 = Embed(
        title="BOT STATUS",
        description="ㅤ",
        color=0x00ff00,
    )
    buttn = ActionRow(
        Button(
            style=ButtonStyle.URL,
            label="github.com",
            url="https://github.com/Tinhdev061"
        )
    )

    cacl = dt.datetime.utcnow()
    embed2.add_field(name="🌐PING", value=f"{round(bot.latency * 1000)} msㅤㅤㅤㅤㅤ", inline=True)
    embed2.add_field(name="🟢UPTIME", value=f"{cacl - startup}", inline=True)
    embed2.add_field(name="Author: ", value="qpneruy (TinhDev061)")
    await ctx.send(embeds=embed2, components=buttn)


def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"


perm_ck = None
queues = NaffQueue
titles = []
audio = None
channelss = None


@slash_command(name="play", description="chơi nhạc")
@interactions.slash_option("song", "Đường dẫn nhạc", 3, True)
async def play(ctx: SlashContext, song: str):
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} > PLAY")
    global perm_ck, queues, titles, audio, channelss
    t = True
    await ctx.defer()
    if not ctx.voice_state:
        if ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()
            channelss = ctx.voice_state.channel.voice_state
            t = True
        else:
            await ctx.send('Bạn phải ở trong 1 kênh thoại', ephemeral=True)
            logger.debug(f'User {ctx.user.display_name} is not in voice channel')
            t = False
    if t:
        if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
            audio = await YTAudio.from_url(song, stream=True)
            title = audio.entry['title']
            titles.append(title)
            queues.put(audio)
            thumbnail = audio.entry['thumbnail']
            uploader = audio.entry['uploader']
            duration = audio.entry['duration']
            embedmusic_inqueue = Embed(
                title=f" {title}",
                description="ㅤ",
                color=0x5f9afa,
            )
            duration_hms = convert_seconds_to_hms(duration)
            embedmusic_inqueue.set_author('➕ Đã Thêm Vào hàng đợi')
            embedmusic_inqueue.set_image(thumbnail)
            embedmusic_inqueue.add_field(name="Upload By:  ", value=f"{uploader}", inline=True)
            embedmusic_inqueue.add_field(name=" Dài:  ", value=f"{duration_hms}", inline=True)
            embedmusic_inqueue.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=embedmusic_inqueue)
            embedmusic_inqueue.set_author('💿 Đang chơi')
            queues.__song_list__.insert(0, embedmusic_inqueue)

        else:
            queues = None
            queues = NaffQueue(channelss)
            perm_ck = ctx.user.id #Kiễm tra người dùng
            audio = await YTAudio.from_url(song, stream=True)
            title = audio.entry['title']
            thumbnail = audio.entry['thumbnail']
            uploader = audio.entry['uploader']
            duration = audio.entry['duration']
            embedmusic = Embed(
                title=f" {title}",
                description="ㅤ",
                color=0x5f9afa,
            )
            duration_hms = convert_seconds_to_hms(duration)
            embedmusic.set_author('📀 Đang Chơi Nhạc')
            embedmusic.set_image(thumbnail)
            embedmusic.add_field(name="Upload By:  ", value=f"{uploader}", inline=True)
            embedmusic.add_field(name=" Dài:  ", value=f"{duration_hms}", inline=True)
            embedmusic.set_thumbnail(url=ctx.author.avatar_url)
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
            await ctx.send(embeds=embedmusic, components=[hang1, hang2])
            embedmusic.set_author('💿 Đang chơi')
            queues.__song_list__.insert(0, embedmusic)
            queues.put(audio)
            queues.start()


@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    global perm_ck, queues
    if ctx.user.id == perm_ck:
        match ctx.custom_id:
            case "pause_button":
                await _pause(ctx)
            case "stop_button":
                await _stop(ctx)
            case "resume_button":
                await _resume(ctx)
            case "vol_up":
                await _volup(ctx)
            case "vol_down":
                await _voldown(ctx)
            case "skip_button":
                await skip(ctx)
            case "loop_button":
                await _loop(ctx)


async def _loop(ctx: SlashContext):
    global queues, audio
    queues.loops()
    await ctx.send("Đã bật lặp")


@slash_command(name="skip", description="Bỏ qua nhạc")
async def _skip(ctx: SlashContext):
    await skip(ctx)


@slash_command(name="stop", description="Dừng Nhạc")
async def __stop(ctx: SlashContext):
    await _stop(ctx)


@slash_command(name="resume", description="Tiếp tục nhạc")
async def __resume(ctx: SlashContext):
    await _resume(ctx)


@slash_command(name="pause", description="tạm dừng nhạc")
async def __pause(ctx: SlashContext):
    await _pause(ctx)


async def skip(self):
    global queues
    logger.debug(f"{self.guild.name}::{self.user.display_name} >:skip \n")
    player = self.bot.get_bot_voice_state(self.guild_id)
    next_item = queues.peek()
    if next_item is not None:
        print(next_item.entry['title'])
        await player.stop()
        await self.voice_state.wait_for_stopped()
    else:
        await self.send("Hết nhạc trong hàng đợi", ephemeral=True)


async def _pause(ctx):
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} >:pause \n")
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send("Đang không phát nhạc")
    else:
        player = ctx.bot.get_bot_voice_state(ctx.guild_id)
        player.pause()
        await ctx.send('Đã tạm dừng', ephemeral=True)


async def _stop(ctx):
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} >:stop \n")
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send("Đang không phát nhạc", ephemeral=True)
    else:
        player = ctx.bot.get_bot_voice_state(ctx.guild_id)
        await player.stop()
        await ctx.send('Đã Dừng', ephemeral=True)


async def _resume(ctx):
    global queues
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} >:resume \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    player.resume()
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send('Đã tiếp tục', ephemeral=True)
    else:
        await ctx.send('Không có nhạc đang dừng', ephemeral=True)


currvol = 0.5


async def _volup(ctx):
    global currvol
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} >:vol_up \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    currvol += 0.1
    player.volume = currvol
    await ctx.send('Đã Tăng âm lượng', ephemeral=True)


async def _voldown(ctx):
    global currvol
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} >:vol_down \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    currvol -= 0.1
    player.volume = currvol
    await ctx.send('Đã Giảm âm lượng', ephemeral=True)


channels = None
channel = None


@listen(VoiceStateUpdate)
async def _join(vs: VoiceStateUpdate):
    global channels, channel
    if vs.after is not None and vs.after.channel.id == channels:
        channel = await vs.after.guild.create_voice_channel(f"Kênh {vs.after.member.display_name} ")
        await vs.after.member.move(channel.id)
    if vs.before is not None and (channel is not None and vs.before.channel.id == channel.id):
        await vs.before.guild.delete_channel(channel.id)
    if vs.before is not None:
        voice_channel = vs.before.channel
        members_in_channel = voice_channel.members
        num_members = len(members_in_channel)
        print(num_members)
        if num_members < 3 and vs.bot.get_bot_voice_state(vs.before.guild) is not None:
            await vs.bot.get_bot_voice_state(vs.before.guild).disconnect()


async def get_remaining_members(channeli):
    members = await channeli.fetch_members()
    num_members = len(members)
    return num_members


@slash_command(name="setup", description="Đặt kênh voiceS")
@slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
async def _setup(ctx: SlashContext, channeli: interactions.OptionType.CHANNEL):
    global channels
    logger.debug(f"{ctx.guild.name}::{ctx.user.display_name} > SETUP  \n")
    channels = channeli.id
    await ctx.send(f"đã đặt kênh {channeli.name} thành kênh voiceS")


bot.start(Token)