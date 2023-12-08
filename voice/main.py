import asyncio
import os
from io import BytesIO

import interactions
import requests
from interactions import File
from interactions import SlashContext, slash_option, slash_command
from interactions.api.events import Startup, MessageCreate
from interactions.api.voice.audio import AudioVolume

from modules import VnEduConnect

Token = os.getenv("Discord_Token_bot_B")
bot = interactions.Client(
    ntents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT, send_command_tracebacks=False,
    sync_interactions=True,
    asyncio_debug=True
)


@interactions.listen(Startup)
async def _starup():
    print(f">> Bot đã khởi Động: {bot.user.display_name}")
    await bot.change_presence(status=interactions.Status.IDLE, activity="lệnh /help để giúp đỡ")


@slash_command(name='pingl', description='dm')
async def record(ctx: interactions.SlashContext):
    voice_state = await ctx.author.voice.channel.connect()

    # Start recording
    await voice_state.start_recording(output_dir="voice_recored")
    await asyncio.sleep(10)
    await voice_state.stop_recording()
    await ctx.send(files=[interactions.File(file, file_name="user_id.mp3") for user_id, file in
                          voice_state.recorder.output.items()])


@interactions.listen()
async def on_message(event: MessageCreate):
    msg = event.message.content
    msg_parts = msg.split(maxsplit=1)
    result = " ".join(msg_parts[1:]) if len(msg_parts) > 1 else ""
    if len(result) < 3:
        await event.message.add_reaction('❌')
        return
    if "_s" in event.message.content:
        await event.message.author.voice.channel.connect()
        url = 'https://api.fpt.ai/hmi/tts/v5'
        headers = {
            'api-key': '12y0uP7g2NK8JlweFlyd49Pk4j2a4eIK',
            'speed': '',
            'voice': 'banmai'
        }
        response = requests.request('POST', url, data=result.encode('utf-8'), headers=headers)
        data = response.json()
        audio = AudioVolume(data["async"])

        audio.ffmpeg_before_args = (
            "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        await event.message.add_reaction('✅')
        await event.message.author.voice.channel.voice_state.play(audio)


@slash_command(name="speak", description="Bot nói")
@slash_option(name="content", description="Nội dung lời nói", opt_type=3, required=True)
async def _speak(ctx: SlashContext, content: str):
    if not ctx.voice_state:
        await ctx.author.voice.channel.connect()
        if ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()

        else:
            await ctx.send('Bạn phải ở trong 1 kênh thoại', ephemeral=True)
    url = 'https://api.fpt.ai/hmi/tts/v5'
    headers = {
        'api-key': '12y0uP7g2NK8JlweFlyd49Pk4j2a4eIK',
        'speed': '',
        'voice': 'banmai'
    }
    response = requests.request('POST', url, data=content.encode('utf-8'), headers=headers)
    data = response.json()
    audio = AudioVolume(data["async"])
    audio.ffmpeg_before_args = (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    )
    await ctx.message.add_reaction('✅')
    await ctx.voice_state.play(audio)


@interactions.slash_command("vnedu", description="Lấy thông tin điểm")
@slash_option(name="phone", description="Số điện thoại của tài khoản", opt_type=3, required=True)
@slash_option(name="passw", description="Mật khẩu tài khoản", opt_type=3, required=True)
@slash_option(name="hocky", description="Nhập học kỳ", opt_type=3, required=True)
@slash_option(name="namhoc", description="Nhập Năm học", opt_type=4, required=True)
async def circle(ctx: SlashContext, phone: str, passw: str, hocky: str, namhoc: int):
    await ctx.defer()
    connect_thread = VnEduConnect()
    img_data = connect_thread.get_diem(phone_number=phone, password=passw, period=int(hocky), year=str(namhoc))
    if img_data[0] == "Code1":
        await ctx.send("Học sinh không tồn tại", ephemeral=True)
    elif img_data[0] == "Code2":
        if "Hiện tại trường đang khóa tra cứu SLL" in img_data[1]:
            await ctx.send(f"Không tồn tại khóa học {namhoc}", ephemeral=True)
        else:
            await ctx.send(img_data[1])
    else:
        img_io = BytesIO(img_data)
        file = File(file=img_io, file_name='bangdiem.png')
        await ctx.send(file=file)


bot.load_extension("db_module")
bot.start(Token)
