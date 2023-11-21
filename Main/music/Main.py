import logging
import os
from datetime import datetime

import interactions
import pymysql
from interactions import ButtonStyle, ActionRow, Button, slash_option
from interactions import SlashContext, listen, slash_command, Embed, OptionType
from interactions.api.events import Startup
from interactions.api.events import VoiceUserJoin, VoiceUserLeave

# Configure the log file and format
formatted_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
log_filename = f'Log/log_{formatted_time}.txt'
log_format = '[%(asctime)s] [%(levelname)s] %(message)s'
date_format = '%H:%M:%S'

# Configure the logger
logger = logging.getLogger('discord_log')
logger.setLevel(logging.DEBUG)

# Configure the file handler
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Configure the stream handler (console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
"""---------------------------------------------------------------------------------"""

api_key = os.getenv('YOUTUBE_API_KEY')
Token = os.getenv("Discord_Token_Bot_A")
"""-----------------------------"""
bot = interactions.Client(
    intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT, send_command_tracebacks=False,
    sync_interactions=True,
    asyncio_debug=True,
    logger=logger)
"""-----------------------------"""


@slash_command(name="refresh_command", description="Làm mới Lệnh")
async def _refresh(ctx: SlashContext):
    bot.reload_extension("play")
    bot.reload_extension("askgpt")
    bot.reload_extension("askbard")
    bot.reload_extension("noi_chu")
    await ctx.send('Đã reset lại command')


@listen(Startup)
async def _starup():
    print(f">> Bot đã khởi Động: {bot.user.display_name}")
    await bot.change_presence(status=interactions.Status.IDLE, activity="lệnh /help để giúp đỡ")


@slash_command(name="help", description="Trợ Giúp")
async def _help(ctx: SlashContext):
    embed = Embed(
        title="**Giúp Đỡ**                       ",
        description="  ",
        color=0x6DAEDB,
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="**📖️ ╏ COMMAND**",
                    value='ㅤ  /about -- Trạng thái bot\nㅤ /Play -- Chơi nhạc\n /ask -- Hỏi bot\n /img -- không dùng')
    await ctx.send(embed=embed)


@slash_command(name="about", description="Trạng Thái Bot")
async def _about(ctx: SlashContext):
    embed = Embed(
        title="-------BOT STATUS-------",
        description="ㅤ",
        color=0x00BAFF,
    )
    button = ActionRow(
        Button(
            style=ButtonStyle.URL,
            label="github.com",
            url="https://github.com/Tinhdev061"
        )
    )

    connect_thread = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
    embed.add_field(name="🏠LOCALHOST PING", value=f"{round(bot.latency * 1000)} msㅤㅤㅤㅤㅤ", inline=True)
    embed.add_field(name="🗃️DATABASE PING", value=f'{connect_thread.ping()} ms')
    embed.add_field(name="⚓CONNECT:", value=f'{connect_thread.get_host_info()}')
    embed.add_field(name="Author: ", value="qpneruy (TinhDev061)")
    await ctx.send(embeds=embed, components=button)


async def get_remaining_members(current_channel):
    members = await current_channel.fetch_members()
    total_members = len(members)
    return total_members


@listen(VoiceUserJoin)
async def __join(vs: VoiceUserJoin):
    connect_thread = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
    try:
        with connect_thread.cursor() as cursor:
            select_query = f"SELECT CAST(voice_id AS SIGNED) FROM server_data WHERE ten_server = '{vs.author.guild.id}'"
            cursor.execute(select_query)
            result = cursor.fetchone()
            if result:
                if vs.channel.id == result[0]:
                    channel_d = await vs.channel.guild.create_voice_channel(f"Kênh {vs.author.display_name}")
                    channel_id = channel_d.id
                    channel_d.user_limit = 10
                    await channel_d.edit(user_limit=5)
                    query = f"INSERT INTO server_{vs.author.guild.id}(active_channel) VALUES ({channel_id}) "
                    cursor.execute(query)
                    connect_thread.commit()
                    mem = vs.author
                    await mem.move(channel_d.id)
            else:
                await vs.author.send('kênh chưa được cài đặt')
    finally:
        connect_thread.close()


@listen(VoiceUserLeave)
async def __leave(vs: VoiceUserLeave):
    conect_thread = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
    cnx = conect_thread.cursor()
    query = f"SELECT CAST(active_channel AS SIGNED) FROM server_{vs.author.guild.id}"
    cnx.execute(query)
    res = cnx.fetchall()
    res_values = [item[0] for item in res]
    if vs.channel.id in res_values:
        await vs.channel.delete()
    query = f"DELETE FROM server_{vs.author.guild.id} WHERE active_channel = {vs.channel.id}"
    cnx.execute(query)
    conect_thread.commit()
    conect_thread.close()


@slash_command(name="setupv", description="Đặt kênh voiceS")
@slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
async def _setup(ctx: SlashContext, channel: interactions.OptionType.CHANNEL):
    connection = pymysql.connect(host='127.0.0.1', user='root', password='', database='discord_guild')
    channels = channel.id
    await ctx.send(f"đã đặt kênh {channel.name} thành kênh voiceS")
    try:
        with connection.cursor() as cursor:
            select_query = f"SELECT * FROM server_data WHERE ten_server = '{ctx.guild_id}'"
            cursor.execute(select_query)
            result = cursor.fetchall()
            if not result:
                print(f"Không tìm thấy server có ten_server = {ctx.guild_id} trong bảng. Thêm mới...")
                new_data = {
                    'ten_server': ctx.guild_id,
                    'voice_id': channels,
                    'gpt_channel_id': 'NULL',
                    'bard_channel_id': 'NULL',
                    'current_vol': 0.5
                }
                insert_data_query = """
                INSERT INTO server_data (ten_server, voice_id, gpt_channel_id, bard_channel_id, current_vol)
                VALUES (%(ten_server)s, %(voice_id)s, %(gpt_channel_id)s, %(bard_channel_id)s, %(current_vol)s)
                """
                cursor.execute(insert_data_query, new_data)
                connection.commit()
                print(f"Đã thêm mới server {ctx.guild_id} vào bảng.")
            else:
                update_query = f"UPDATE server_data SET voice_id = '{channels}' WHERE ten_server = '{ctx.guild_id}'"
                cursor.execute(update_query)
                connection.commit()
                print(f"Đã cập nhật giá trị voice_id cho server {ctx.guild_id}.")
    finally:
        connection.close()


# @slash_command(name="stop_bot", description="Dừng bot mode An toàn")
# async def _stop_():
#     await bot.stop()


bot.load_extension("play")
bot.load_extension("askgpt")
bot.load_extension("askbard")
bot.load_extension("noi_chu")
bot.load_extension("db_refesh")
bot.start(Token)
