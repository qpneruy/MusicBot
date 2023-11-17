import os
import json
import logging
import aiohttp
import pymysql
import datetime
import interactions
from interactions import SlashContext, listen, slash_command, Embed, OptionType
from interactions.api.events import VoiceUserJoin, VoiceUserLeave
from interactions import ButtonStyle, ActionRow, Button, slash_option
from interactions.api.events import Startup, MessageCreate

"""---------------------------------------------------------------------------------"""

api_key = os.getenv('YOUTUBE_API_KEY')
Token = os.getenv("Discord_Token_Bot_A")

"""-----------------------------"""
# Cấu hình cho module Logging
now = datetime.datetime.now()
formatted_time = now.strftime('%Y-%m-%d_%H-%M')
log_filename = f'Log//log_{formatted_time}.txt'
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
startup = datetime.datetime.utcnow()
"""-----------------------------"""

"""-----------------------------"""
bot = interactions.Client(
    intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT, send_command_tracebacks=False)

model_data = {
    "history": {
        "word_list": [],
        "previous_user": "None",
    },
    "current": "None",
}
"""-----------------------------"""


@listen()
async def on_message(event: MessageCreate):
    if event.message.author.id == event.bot.user.id:
        return
    async with aiohttp.ClientSession() as session:
        with pymysql.connect(host=host, user='root', password=password, database=database) as connect_thread:
            with connect_thread.cursor() as cnx:
                query = "SELECT CAST(word_connect_id AS SIGNED) FROM server_data WHERE ten_server = %s"
                cnx.execute(query, (event.message.author.guild.id,))
                data = cnx.fetchone()
                data = data[0] if data else None
                # Kiễm tra id channel | kiểm tra có tồn tại từ hay không
                if data != event.message.channel.id:
                    return
        user_word = event.message.content
        user_word = user_word.lower()
        async with session.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{user_word}") as response:
            api_data = await response.json()
        if ("title" in api_data) or (' ' in user_word):
            await event.message.add_reaction('❌')
            await event.message.channel.send(f"Từ `{user_word}` Không Tồn tại trong từ điển của bot")
            return
        """---------------------------------------------------------------------------"""
        # load dữ liệu từ file data thuộc mỗi ctx.guild.id
        with open(f"json/word_data_sv_{event.message.author.guild.id}", "r") as datafile:
            data = json.load(datafile)
        previous_word = data["current"]
        """---------------------------------------------------------------------------"""
        # kiểm tra người nối từ hiện tại đã nối từ trước đó hay không
        # if data["history"]["previous_user"] == event.message.author.id:
        #     await event.message.channel.send("Bạn đã nối từ trước đó rồi")
        #     await event.message.add_reaction('❌')
        #     return
        """---------------------------------------------------------------------------"""
        # kiểm tra xem từ đã được nối trước đó hay chưa
        if user_word in data["history"]["word_list"]:
            await event.message.channel.send(f"Từ `{user_word}` Đã có người nối trước")
            await event.message.add_reaction('❌')
            return
        """---------------------------------------------------------------------------"""
        # kiểm tra xem ký tự cuối của chữ này có bằng ký tự đầu của chữ kia không
        # Đồng thời nếu thỏa mãn thì lưu dữ liệu lại
        if user_word[0] == previous_word[len(previous_word) - 1] or previous_word == "None":
            await event.message.add_reaction('✅')
            data["current"] = user_word
            data["history"]["word_list"].append(user_word)
            data["history"]["previous_user"] = event.message.author.id
            with open(f"json/word_data_sv_{event.message.author.guild.id}", "w") as datafile:
                json.dump(data, datafile, indent=4)
        else:
            await event.message.channel.send(
                f"Từ `{user_word}` Không bắt đầu bằng ký tự `{previous_word[len(previous_word) - 1]}`")
            await event.message.add_reaction('❌')


@slash_command(name="reset_noi_chu", description="Xóa dữ liệu")
async def _reset(ctx: SlashContext):
    global model_data
    with open(f"json/word_data_sv_{ctx.guild.id}", "w") as datafile:
        json.dump(model_data, datafile, indent=4)
    await ctx.send(f"↩️ Đã reset nối chữ")


@slash_command(name="word_setup", description="Đặt kênh nối chữ")
@slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
async def _world_setup(ctx: SlashContext, channel: OptionType.CHANNEL):
    global model_data
    with open(f'json/word_data_sv_{ctx.guild.id}', 'w') as f:
        json.dump(model_data, f, indent=4)
    await ctx.send(f'Đã Đặt kênh {channel.name} thành kênh nối chữ')
    ctx = channel
    await ctx.send('✅ Bắt đầu chơi')


@slash_command(name="rs", description="rs")
async def rs(ctx: SlashContext):
    bot.reload_extension("play")
    bot.reload_extension("gpt")
    bot.reload_extension("bard")
    await ctx.send('Đã reset lại command')


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

    connect_thread = pymysql.connect(host=host, user='root', password=password, database=database)
    embed.add_field(name="🏠LOCALHOST PING", value=f"{round(bot.latency * 1000)} msㅤㅤㅤㅤㅤ", inline=True)
    embed.add_field(name="🤖API OPEN AI", value=f'{end_time - start_time} Giây')
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
    connect_thread = pymysql.connect(host=host, user='root', password=password, database=database)
    try:
        with connect_thread.cursor() as cursor:
            select_query = f"SELECT CAST(voice_id AS SIGNED) FROM server_data WHERE ten_server = '{vs.author.guild.id}'"
            cursor.execute(select_query)
            result = cursor.fetchone()
            if result:
                if vs.channel.id == result[0]:
                    channel_d = await vs.channel.guild.create_voice_channel(f"Kênh {vs.author.display_name}")
                    channel_id = channel_d.id
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
    conect_thread = pymysql.connect(host=host, user='root', password=password, database=database)
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


host = 'localhost'
password = ''
database = 'discord_guild'


@slash_command(name="setupv", description="Đặt kênh voiceS")
@slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
async def _setup(ctx: SlashContext, channel: interactions.OptionType.CHANNEL):
    connection = pymysql.connect(host=host, user='root', password=password, database=database)
    logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > SETUP  \n")
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


# Kiễm tra xem bảng có tồn tại trong database không
def table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None


# Lấy tên tất cả các bảng trong database
def get_all_tables(cursor, database_name):
    cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{database_name}'")
    return [table[0] for table in cursor.fetchall()]


@slash_command(name='db_refreshv2', description="Làm mới cơ sở dữ liệu (xóa)")
async def dbv2_command(ctx: SlashContext):
    guild_ids = [str(guild.id) for guild in ctx.bot.guilds]
    conect_thread = pymysql.connect(host=host, user='root', password=password, database=database)
    cursor = conect_thread.cursor()
    current_list = get_all_tables(cursor, 'discord_guild')
    for table_name in current_list:
        if table_name.startswith('server_') and table_name[7:] not in guild_ids:
            query = f"DROP TABLE {table_name}"
            if table_name != 'server_data':
                cursor.execute(query)
    conect_thread.commit()
    conect_thread.close()
    await ctx.send('Đã làm mới cơ sở dữ liệu phương thức xóa')


@slash_command(name='db_refreshv1', description="Làm mới cơ sở dữ liệu (tạo)")
async def dbv1_command(ctx: SlashContext):
    guilds = ctx.bot.guilds
    connection = pymysql.connect(host=host, user='root', password=password, database=database)
    create_table_query = """
        CREATE TABLE IF NOT EXISTS server_data (
            ten_server VARCHAR(255) NOT NULL,
            voice_id VARCHAR(255) NOT NULL,
            gpt_channel_id VARCHAR(255) NOT NULL,
            bard_channel_id VARCHAR(255) NOT NULL,
            current_vol DOUBLE NOT NULL
        )
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    for guild in guilds:
        if not table_exists(cursor, f'server_{guild.id}'):
            query = f"CREATE TABLE server_{guild.id}(active_channel VARCHAR(255) not NULL)"
            cursor.execute(query)
        select_query = f"SELECT * FROM server_data WHERE ten_server = {guild.id}"
        cursor.execute(select_query)
        result = cursor.fetchall()
        if result:
            print(f"Giá trị {guild.id} tồn tại trong cột 'ten_server'.")
        else:
            print(f"Giá trị {guild.id} đã được thêm.")
            new_data = {
                'ten_server': guild.id,
                'voice_id': 'NULL',
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
    connection.close()
    await ctx.send('Đã làm mới cơ sở dữ liệu phương thức tạo')


bot.load_extension("play")
bot.load_extension("gpt")
bot.load_extension("bard")
bot.start(Token)
