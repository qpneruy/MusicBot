import os
import base64
import os

import interactions
import requests
from easy_pil import Editor, load_image_async
from interactions import SlashContext, slash_command, slash_option
from interactions.api.events import MessageCreate
from interactions.api.voice.audio import AudioVolume
from nextcord import Intents
from nextcord.ext.commands import Bot

Token = os.getenv("Discord_Token_bot_B")
bot = interactions.Client(
    intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT, send_command_tracebacks=False
)

bot1 = Bot(command_prefix='!', intents=Intents.all())


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


def convert_image_to_rgb(image):
    if image.mode == "RGBA":
        rgb_image = image.convert("RGB")
        return rgb_image
    else:
        return image


@slash_command(name="circle", description="Bot nói")
async def _circle(ctx: SlashContext):
    # Load the image using `load_image_async` method
    image = await load_image_async(ctx.author.avatar_url)

    # Convert the image to RGB mode
    rgb_image = convert_image_to_rgb(image)

    # Initialize the editor and pass image as a parameter
    editor = Editor(rgb_image).circle_image()
    image_data = image.tobytes()
    encoded_image_data = base64.b64encode(image_data)
    # Creating nextcord.File object from image_bytes from editor
    # file = interactions.open_file(editor.image_bytes)

    await ctx.send(encoded_image_data)


# bot1.run(Token)

# Start the bot
bot.start(Token)
