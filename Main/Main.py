import os
import time
import requests
import datetime as dt
import interactions
from interactions import SlashContext, listen, slash_command, Embed, OptionType, slash_option, \
    ButtonStyle, ActionRow, Button
from interactions.models.discord.channel import ThreadChannel  # phát triển code sử dụng module threadchannel
from interactions.api.events import Startup, VoiceStateUpdate, Component, MessageCreate  # dùng VoiceUserLeave để lắng
import google.generativeai as palm
from Queue import NaffQueue
from yt_download import YTAudio
import logging
import datetime
import openai
import json
import video_info

gpt = os.getenv("OPENAI_API_KEY")
bard = os.getenv("PALM_API_KEY")
api_key = os.getenv('YOUTUBE_API_KEY')
palm.configure(api_key=bard)
openai.api_key = gpt

messages = [{"role": "system", "content":
    "You are a intelligent assistant."}]

now = datetime.datetime.now()
formatted_time = now.strftime('%Y-%m-%d_%H-%M')
log_filename = f'log_{formatted_time}.txt'
logger = logging.getLogger('discord_log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_filename, encoding='utf-8')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

Token = os.getenv("Discord_Token_Bot_A")
# Token = os.getenv("Discord_Token_bot_B")
# bot = interactions.Client()
startup = dt.datetime.utcnow()

Client: interactions.Client = interactions.Client(
    send_command_tracebacks=False,
)
bot = interactions.Client(
    intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT)  # specifically message content,


# not just messages


# @interactions.listen()
# async def on_message_create(event: MessageCreate):
#     print(event.message.channel.id)
#     print(event.message.content)


@listen(Startup)
async def _starup():
    logger.debug(f" >> Bot Da Hoat dong! Ten: {bot.user.display_name}")
    await bot.change_presence(status=interactions.Status.IDLE, activity="lệnh /help để giúp đỡ")


@slash_command(name="help", description="Trợ Giúp")
async def _help(ctx: SlashContext):
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > HELP")
    embed = Embed(
        title="**Giúp Đỡ**                       ",
        description="  ",
        color=0x6DAEDB,
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="**📖️ ╏ COMMAND**",
                    value='ㅤ  /about -- Trạng thái bot\nㅤ /Play -- Chơi nhạc\n /ask -- Hỏi bot\n /img -- không dùng')
    await ctx.send(embed=embed)


end_time = 0.0
start_time = 0.0


@slash_command(name="about", description="Trạng Thái Bot")
async def _about(ctx: SlashContext):
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > ABOUT")
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
    embed2.add_field(name="🤖API Phản hồi", value=f'{end_time - start_time} Giây')
    embed2.add_field(name="Author: ", value="qpneruy (TinhDev061)")
    await ctx.send(embeds=embed2, components=buttn)


@slash_command(name="askbard", description="Hỏi Palm 1 câu hỏi")
@interactions.slash_option(
    name="content",
    description="Nội dung câu hỏi",
    opt_type=3,
    required=True,
)
# @slash_option(
#     name="vai",
#     description="Tôi nên trả lời thế nào",
#     opt_type=3,
#     required=False,
# )
async def _askbard(ctx: SlashContext, content: str):
    global mes
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > ASKBARD: {content}")
    await ctx.defer()
    if mes is None:
        mes = palm.chat(messages=content)
    else:
        mes = mes.reply(message=content)
    if mes.last is None:
        await _endbard(ctx)
    else:
        await ctx.send(f'**{ctx.user.display_name}**: {content} \n **bard:** {mes.last}')


@slash_command(name="endbard", description="kết thúc chủ đề")
async def _endbard(ctx: SlashContext):
    global mes
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > ENBARD: ")
    formatted_t = now.strftime('%Y-%m-%d_%H-%M')
    with open(formatted_t + '.json', "w") as f:
        json.dump(mes.messages, f)
    mes = None
    await ctx.send("Đã kết thúc chủ đề")


mes = None


@slash_command(name="askgpt", description="Hỏi gpt 1 câu hỏi")
@interactions.slash_option(
    name="content",
    description="nội dung câu hỏi",
    opt_type=3,
    required=True
)
async def _askgpt(ctx: SlashContext, content: str):
    global end_time, start_time
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > ASKGPT: {content}")
    await ctx.defer()
    if len(content) <= 2000:
        message = content
        start_time = time.time()
        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            reply = chat.choices[0].message.content
            if len(reply) > 2000:
                await ctx.send('câu trả lời quá dài vui lòng hỏi câu hác :))')
            else:
                end_time = time.time()
                await ctx.send(
                    f'**{ctx.user.display_name}:** {content}\n**qpneruy:** {reply}\n||Response Time: {end_time - start_time} seconds||')

        messages.append({"role": "assistant", "content": reply})
    else:
        await ctx.send("tin nhắn quá 2000 ký tự", ephemeral=True)


@slash_command(name='img', description="Tạo ảnh theo mô tả")
@interactions.slash_option("prompt", "mô tả ảnh", 3, True)
async def _img(ctx: SlashContext, prompt: str):
    if ctx.author == bot.owners:
        await ctx.defer()
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024X1024"
        )
        image_url = response['data'][0]['url']
        await ctx.send(image_url)


@slash_command(name="menu", description="Menu chơi nhạc")
async def _menu(ctx: SlashContext):
    global hang2, hang1
    await ctx.send(components=[hang1, hang2])


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

queues = NaffQueue
videoinfo = video_info.VideoInfo()


def get_avt_audio(audio_d):
    search_query = audio_d.entry['title']
    url_video = videoinfo.search_vid(search_query)
    return videoinfo.get_uploader_avt(url_video)


@slash_command(name="play", description="chơi nhạc")
@interactions.slash_option("song", "Đường dẫn nhạc & Tên bài hát", 3, True)
async def play(ctx: SlashContext, song: str):
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > PLAY ")
    global queues, videoinfo
    global hang2, hang1, api_key
    current_channel = None
    User_inVoice = True
    await ctx.defer()
    ppl_url = "https://www.youtube.com/playlist?list="
    if not ctx.voice_state:
        if ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()
            current_channel = ctx.voice_state.channel.voice_state
            User_inVoice = True
            queues = NaffQueue(current_channel)
            videoinfo = video_info.VideoInfo()
        else:
            await ctx.send('Bạn phải ở trong 1 kênh thoại', ephemeral=True)
            logger.debug(f'User {ctx.user.display_name} is not in voice channel')
            User_inVoice = False
    if ppl_url in song:
        list_url = await videoinfo.playlist_get(song)
        while videoinfo.peek():
            link = list_url.pop()
            print('alo')
            audio = await YTAudio.from_url(link, stream=True)
            avatar_url = videoinfo.get_uploader_avt(link)
            queues.put(audio, avatar_url)
        await ctx.send("Thêm danh sách thành công", ephemeral=True)
        queues.start()
    elif User_inVoice:
        if ctx.voice_state is not None and ctx.voice_state.channel.voice_state.playing is True:
            audio = await YTAudio.from_url(song, stream=True)
            avatar_url = get_avt_audio(audio)

            queues.put(audio, avatar_url)
            embed = queues.__song_list__[0]
            embed.set_author('➕ Đã Thêm Vào hàng đợi')
            await ctx.send(embed=embed)
        else:
            queues = NaffQueue(current_channel)
            videoinfo = video_info.VideoInfo()
            if "https://www.youtube.com/watch?v=" in song or "https://youtu.be/" in song:
                audio = await YTAudio.from_url(song, stream=True)
                avatar_url = videoinfo.get_uploader_avt(song)
                queues.put(audio, avatar_url)
            else:
                audio = await YTAudio.from_url(song, stream=True)
                avatar_url = get_avt_audio(audio)
                queues.put(audio, ctx, avatar_url)
            embed = queues.__song_list__[0]
            embed.set_author('📀 Đang Chơi Nhạc')
            await ctx.send(embeds=embed, components=[hang1, hang2])
            queues.start()


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
        case "vol_up":
            await _volup(ctx)
        case "vol_down":
            await _voldown(ctx)
        case "skip_button":
            await _skip(ctx)
        # case "loop_button":
        #     await _loop(ctx)


@slash_command(name="skip", description="Bỏ qua nhạc")
async def _skip(self: SlashContext):
    global queues
    logger.debug(f"[{self.guild.name}]::{self.user.display_name}] >skip \n")
    player = self.bot.get_bot_voice_state(self.guild_id)
    next_item = queues.peek()
    if next_item is not None:
        await player.stop()
        await self.send('Đã skip', ephemeral=True)
        await self.voice_state.wait_for_stopped()
    else:
        await self.send("Hết nhạc trong hàng đợi", ephemeral=True)


@slash_command(name="stop", description="Dừng Nhạc")
async def _stop(ctx):
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >stop \n")
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send("Đang không phát nhạc", ephemeral=True)
    else:
        player = ctx.bot.get_bot_voice_state(ctx.guild_id)
        await player.stop()
        await ctx.send('Đã Dừng', ephemeral=True)


@slash_command(name="resume", description="Tiếp tục nhạc")
async def _resume(ctx):
    global queues
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >resume \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    player.resume()
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send('Đã tiếp tục', ephemeral=True)
    else:
        await ctx.send('Không có nhạc đang dừng', ephemeral=True)


@slash_command(name="pause", description="tạm dừng nhạc")
async def _pause(ctx):
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >pause \n")
    if ctx.voice_state.channel.voice_state.playing is not True:
        await ctx.send("Đang không phát nhạc")
    else:
        player = ctx.bot.get_bot_voice_state(ctx.guild_id)
        player.pause()
        await ctx.send('Đã tạm dừng', ephemeral=True)


currvol = 0.5


async def _volup(ctx):
    global currvol
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >vol_up \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    currvol += 0.1
    player.volume = currvol
    await ctx.send('Đã Tăng âm lượng', ephemeral=True)


async def _voldown(ctx):
    global currvol
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: >vol_down \n")
    player = ctx.bot.get_bot_voice_state(ctx.guild_id)
    currvol -= 0.1
    player.volume = currvol
    await ctx.send('Đã Giảm âm lượng', ephemeral=True)


channels = None
channel = None


async def get_remaining_members(channeli):
    members = await channeli.fetch_members()
    num_members = len(members)
    return num_members


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
        if num_members < 3 and vs.bot.get_bot_voice_state(vs.before.guild) is not None:
            await vs.bot.get_bot_voice_state(vs.before.guild).disconnect()


@slash_command(name="setup", description="Đặt kênh voiceS")
@slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
async def _setup(ctx: SlashContext, channeli: interactions.OptionType.CHANNEL):
    global channels
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > SETUP  \n")
    channels = channeli.id
    await ctx.send(f"đã đặt kênh {channeli.name} thành kênh voiceS")


bot.start(Token)
