import os
import asyncio
import datetime as dt
import interactions
from typing_extensions import Self
import random
from collections import deque
from typing import Iterator
from yt_dlp import YoutubeDL
from interactions import SlashContext, listen, slash_command, Embed, OptionType, slash_option, ActiveVoiceState, Button, \
    ButtonStyle, ActionRow, Button
from interactions.api.events import Startup, BaseVoiceEvent, VoiceStateUpdate, Component
from interactions.api.voice.audio import AudioVolume, BaseAudio

Token = os.getenv("Discord_Token_bot_A")
#Token = os.getenv("Discord_Token_bot_B")
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

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self._item_queued = asyncio.Event()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    def put(self, audio: BaseAudio) -> None:
        self._entries.append(audio)
        self._item_queued.set()

    def put_first(self, audio: BaseAudio) -> None:
        self._entries.appendleft(audio)
        self._item_queued.set()

    async def pop(self) -> BaseAudio:
        if len(self) == 0:
            await self._item_queued.wait()
        item = self._entries.popleft()
        self._item_queued.clear()
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
            audio = await self.pop()
            await self.voice_state.play(audio)

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        asyncio.create_task(self())

    async def skip(self):
        if len(self._entries) > 0:
            self._entries.popleft()  # Loại bỏ bài hát đầu tiên khỏi hàng đợi

        if len(self._entries) > 0:
            next_audio = self._entries[0]  # Lấy bài hát tiếp theo từ hàng đợi
            await self.voice_state.play(next_audio)  # Bắt đầu phát bài hát tiếp theo

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
    print(f" >> Bot Da Hoat dong! Ten: {bot.user.display_name}")


@slash_command(name="help", description="Trợ Giúp")
async def _help(ctx: SlashContext):
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
    embed2 = Embed(
        title="BOT STATUS",
        description="ㅤ",
        color=0x00ff00,
    )
    cacl = dt.datetime.utcnow()
    embed2.add_field(name="🌐PING", value=f"{round(bot.latency * 1000)} msㅤㅤㅤㅤㅤ", inline=True)
    embed2.add_field(name="🟢UPTIME", value=f"{cacl - startup}", inline=True)
    await ctx.send(embeds=embed2)

def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"


perm_ck = None
queues = NaffQueue(None)
titles = []
@slash_command(name="playlist", description="Xem danh sách nhạc trong hàng đợi")
async def _playlist(ctx: SlashContext):
    i = 0
    for x in titles:
        i += 1
        await ctx.send(f"{i} -- {x}")
@slash_command(name="doi", description="Thêm nhạc vào hàng đợi")
@interactions.slash_option("song", "Đường dẫns nhạc", 3, True)
async def _doi(ctx: SlashContext, song: str):
    global queues
    if not ctx.responded:
        await ctx.defer()
    audio = await YTAudio.from_url(song, stream=True)
    queues.put(audio)
    title = audio.entry['title']
    titles.append(title)
    await ctx.send(f"Thêm {title} vào hàng đợi thành công", ephemeral=True)


@slash_command(name="play", description="chơi nhạc")
@interactions.slash_option("song", "Đường dẫn nhạc", 3, True)
async def play(ctx: SlashContext, song: str):
    global perm_ck, queues, titles
    titles = []
    perm_ck = ctx.user.id
    if not ctx.voice_state:
        await ctx.author.voice.channel.connect()
    await ctx.defer()
    audio = await YTAudio.from_url(song, stream=True)
    title = audio.entry['title']
    titles.append(title)
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
            style=ButtonStyle.URL,
            label="Youtube",
            url=song,
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
    embedmusic.add_field(name="Tình Đẹp Trai", value="  ")
    channel = ctx.voice_state.channel.voice_state
    queues = NaffQueue(channel)
    queues.put(audio)
    queues.start()
    await ctx.send(embeds=embedmusic, components=[hang1, hang2])

#   await ctx.send(f"_2>>{ctx.voice_state.channel.voice_state.playing}")
#   task = asyncio.create_task(ctx.voice_state.play(audio))
# #  await ctx.send(f"1>>{ctx.voice_state.channel.bot.get_bot_voice_state(ctx.guild_id)}")
#   await ctx.send(f"2>>{ctx.voice_state.channel.voice_state.playing}")


@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    global perm_ck, queues
    if ctx.user.id == perm_ck:
        match ctx.custom_id:
            case "pause_button":
                await _pause(ctx)
            case "stop_button":
                await ctx.send("nope")
                await _stop(ctx)
            case "resume_button":
                await _resume(ctx)
            case "vol_up":
                await _volup(ctx)
            case "vol_down":
                await _voldown(ctx)
            case "skip_button":
                await skip(ctx)


async def skip(self):
    global queues
    play = self.bot.get_bot_voice_state(self.guild_id)
    await play.stop()
    queues.start()
    if self.voice_state.channel.voice_state.playing is not True:
        await self.send("Hết nhạc trong hàng đợi", ephemeral=True)


async def _pause(ctx):
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send("Đang không phát nhạc")
    else:
      play = ctx.bot.get_bot_voice_state(ctx.guild_id)
      play.pause()
      await ctx.send('Đã tạm dừng', ephemeral=True)

async def _stop(ctx):
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send("Đang không phát nhạc", ephemeral=True)
    else:
      play = ctx.bot.get_bot_voice_state(ctx.guild_id)
      await play.stop()
      await ctx.send('Đã Dừng', ephemeral=True)


async def _resume(ctx):
      play = ctx.bot.get_bot_voice_state(ctx.guild_id)
      play.resume()
      await ctx.send('Đã tiếp tục', ephemeral=True)


currvol = 0.5

async def _volup(ctx):

    global currvol
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    currvol += 0.2
    play.volume = currvol
    await ctx.send('Đã Tăng âm lượng', ephemeral=True)


async def _voldown(ctx):
    global currvol
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    currvol -= 0.2
    play.volume = currvol
    await ctx.send('Đã Tăng âm lượng', ephemeral=True)

channels = None
@listen(VoiceStateUpdate)
async def _join(vs: VoiceStateUpdate):
    global channel, channels
    if vs.after is not None and vs.after.channel.id == channels:
        channel = await vs.after.guild.create_voice_channel(f"Kênh {vs.after.member.display_name} ")
        await vs.after.member.move(channel.id)
    if vs.before is not None and vs.before.channel.id == channel.id:
        await vs.before.guild.delete_channel(channel.id)
        channel = None
@slash_command(name="setup", description="Đặt kênh voiceS")
@slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
async def _setup(ctx: SlashContext, channel: interactions.OptionType.CHANNEL):
    global channels
    channels = channel.id
    await ctx.send(f"đã đặt kênh {channel.name} thành kênh voiceS")
bot.start(Token)
