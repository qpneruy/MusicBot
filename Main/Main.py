import os
import asyncio
import datetime as dt
import interactions
from typing_extensions import Self
import yt_dlp
from yt_dlp import YoutubeDL
from interactions import SlashContext,listen, slash_command, Embed, OptionType, slash_option,  ActiveVoiceState
from interactions.api.events import Startup
from interactions.api.voice.audio import AudioVolume
from interactions import Button, ButtonStyle, ActionRow, Button
from interactions.api.events import Component
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
   player.stop()
def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"
@slash_command(name="test", description="test")
async def _test(ctx: SlashContext):
    button = Button(
        custom_id="my_button_id",
        style=ButtonStyle.GREEN,
        label="Click Me",
    )
    message = await ctx.send("Look a Button!", components=button)


@slash_command(name="play",description="chơi nhạc")
@interactions.slash_option("song", "Đường dẫn nhạc", 3, True)
async def play(ctx: SlashContext, song: str):
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
    duration_hms = convert_seconds_to_hms(duration)
    embedmusic.set_author('📀 Đang Chơi Nhạc')
    embedmusic.set_image(thumbnail)
    embedmusic.add_field(name="Upload By:  ", value= f"{uploader}", inline=True)
    embedmusic.add_field(name=" Dài:  ", value=f"{duration_hms}", inline=True)
    embedmusic.set_thumbnail(url=ctx.author.avatar_url)
    component: list[ActionRow] = [
        ActionRow (
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
    ]
    await ctx.send(embeds=embedmusic, components=component)
    await ctx.voice_state.play(audio)
@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx

    match ctx.custom_id:
        case "pause_button":
            await _pause(ctx)
        case "stop_button":
            await _stop(ctx)
        case "resume_button":
            await _resume(ctx)
async def _pause(ctx):
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    play.pause()
    await ctx.send('Đã tạm dừng')
async def _stop(ctx):
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    play.stop()
    await ctx.send('Đã dừng')
async def _resume(ctx):
    play = ctx.bot.get_bot_voice_state(ctx.guild_id)
    play.resume()
    await ctx.send('Đã tiếp tục')

bot.start(Token)