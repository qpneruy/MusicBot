import os
import array as arr
import asyncio
import datetime as dt
import interactions
from typing_extensions import Self
import random
from collections import deque
from typing import Iterator
from yt_dlp import YoutubeDL
from interactions import SlashContext,listen, slash_command, Embed, OptionType, slash_option,  ActiveVoiceState,  Button, ButtonStyle, ActionRow, Button
from interactions.api.events import Startup, BaseVoiceEvent, VoiceStateUpdate, Component
from interactions.api.voice.audio import AudioVolume, BaseAudio
Token = os.getenv("Discord_Token_bot_A")
print(Token)
bot = interactions.Client();
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
    """The voice state this queue is playing for."""
    _entries: deque
    """The queue's base data store"""
    _item_queued: asyncio.Event
    """An event to be fired whenever an item is queued."""
    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self._item_queued = asyncio.Event()
    def __len__(self) -> int:
        return len(self._entries)
    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)
    def put(self, audio: BaseAudio) -> None:
        """
        Enqueue audio at the end of the queue.

        Args:
            audio: The audio to enqueue
        """
        self._entries.append(audio)
        self._item_queued.set()
    def put_first(self, audio: BaseAudio) -> None:
        """
        Enqueue Audio to be played next.
        Args:
            audio: The audio to enqueue
        """
        self._entries.appendleft(audio)
        self._item_queued.set()
    async def pop(self) -> BaseAudio:
        """
        Pop the next item from the queue.
        Will wait if there are no items in the queue.
        """
        if len(self) == 0:
            # wait for an item to be enqueued
            await self._item_queued.wait()
        item = self._entries.popleft()
        self._item_queued.clear()
        return item
    def pop_no_wait(self) -> BaseAudio:
        """Pop from the queue without waiting."""
        return self._entries.popleft()
    def shuffle(self) -> None:
        """Shuffle the queue."""
        random.shuffle(self._entries)

    def clear(self) -> None:
        """Clear the queue."""
        self._entries.clear()

    def peek(self, positions: int = 1) -> BaseAudio | None:
        """
        Peek ahead `position` in the queue.

        Args:
            positions: How many positions ahead to peek at.

        Returns:
            BaseAudio if anything at the given position
        """
        try:
            return self._entries[positions - 1]
        except IndexError:
            return None
    def peek_at_index(self, index: int) -> BaseAudio:
        """
        Peek at a specific Index
        Args:
            index: The index to peek at
        Returns:
            BaseAudio at given index
        """
        return self._entries[index]
    async def __playback_queue(self) -> None:
        """The queue task itself. While the vc is connected, it will play through the enqueued audio"""
        while self.voice_state.connected:
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            audio = await self.pop()
            await self.voice_state.play(audio)
    async def __call__(self) -> None:
        await self.__playback_queue()
    def start(self) -> None:
        """Create a background Queue task"""
        asyncio.create_task(self())
class YTAudio(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None
        """The audio entry this audio object represents."""

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

    cacl = dt.datetime.utcnow();
    embed2.add_field(name="🌐PING", value= f"{round(bot.latency*1000)} msㅤㅤㅤㅤㅤ", inline=True )
    embed2.add_field(name="🟢UPTIME",value=f"{cacl-startup}", inline=True)
    await ctx.send(embeds=embed2)
@slash_command(name="stop", description="Dừng Nhạc")
async def _stop(ctx: SlashContext):
   player = ctx.bot.get_bot_voice_state(ctx.guild_id)
   await player.stop()
def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"
perm_ck = None
@slash_command(name="play",description="chơi nhạc")
@interactions.slash_option("song", "Đường dẫn nhạc", 3, True)
async def play(ctx: SlashContext, song: str):
    global perm_ck
    perm_ck = ctx.user.id
    if not ctx.voice_state:
        await ctx.author.voice.channel.connect()
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
    music_list = []
    duration_hms = convert_seconds_to_hms(duration)
    embedmusic.set_author('📀 Đang Chơi Nhạc')
    embedmusic.set_image(thumbnail)
    embedmusic.add_field(name="Upload By:  ", value= f"{uploader}", inline=True)
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
    # if ctx.voice_state not in queues:
    #     queues[ctx.voice_state] = NaffQueue(ctx.voice_state)
    # queue = queues[ctx.voice_state]
    # audio = await YTAudio.from_url(song, stream=True)
    # queue.put(audio)
    global bot
    await ctx.send(embeds=embedmusic, components=[hang1, hang2])
    await ctx.voice_state.play(audio)

@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    global perm_ck
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
#        case "skip_button":

async def _pause(ctx):
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    play.pause()
    await ctx.send('Đã tạm dừng', ephemeral=True)
async def _stop(ctx):
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    play.stop()
    await ctx.send('Nhấn CC')
async def _resume(ctx):
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    play.resume()
    await ctx.send('Đã tiếp tục', ephemeral=True)
currvol = 0.5;
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
@listen(VoiceStateUpdate)
async def _join(vs: VoiceStateUpdate):
    global channel
    if vs.after is not None and (vs.after.channel.id == 1159792966873907200 or vs.after.channel.id == 1149195429964152895):
      channel = await vs.after.guild.create_voice_channel(f"Kênh {vs.after.member.display_name} ")
      await vs.after.member.move(channel.id)
    if vs.before is not None and vs.before.channel.id == channel.id:
        await vs.before.guild.delete_channel(channel.id)
        channel = None
bot.start(Token)