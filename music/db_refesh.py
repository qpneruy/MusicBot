import pymysql
from interactions import Extension, slash_command, SlashContext


# Kiễm tra xem bảng có tồn tại trong database không
def table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None


def get_all_tables(cursor, database_name):
    cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{database_name}'")
    return [table[0] for table in cursor.fetchall()]


class Database(Extension):
    host = 'localhost'
    password = 'W2:)G8%ZLj~8'
    database = 'discord_guild'

    # Lấy tên tất cả các bảng trong database
    @slash_command(name='db_refreshv2', description="Làm mới cơ sở dữ liệu (xóa)")
    async def dbv2_command(self, ctx: SlashContext):
        guild_ids = [str(guild.id) for guild in ctx.bot.guilds]
        conect_thread = pymysql.connect(host=self.host, user='root', password=self.password, database=self.database)
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
    async def dbv1_command(self, ctx: SlashContext):
        guilds = ctx.bot.guilds
        connection = pymysql.connect(host=self.host, user='root', password=self.password, database=self.database)
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
        with pymysql.connect(host='127.0.0.1', user='root', password='W2:)G8%ZLj~8',
                             database='discord_voice') as connect_thread:
            cursor = connect_thread.cursor()
            guilds = ctx.bot.guilds
            for guild in guilds:
                select_query = f"SELECT * FROM server_data WHERE guild_id = {guild.id}"
                cursor.execute(select_query)
                result = cursor.fetchall()
                print('>>>>>>>>>>', result)
                if result:
                    print(f"Giá trị {guild.id} tồn tại trong cột 'ten_server'.")
                else:
                    print(f"Giá trị {guild.id} đã được thêm.")
                    insert_data_query = """
                        INSERT INTO server_data (guild_id, record_state)
                        VALUES (%(guild_id)s, %(record_state)s)
                        """
                    cursor.execute(insert_data_query, {'guild_id': guild.id, 'record_state': False})
                cursor.execute(select_query)
            connect_thread.commit()
        await ctx.send('Đã làm mới cơ sở dữ liệu phương thức tạo')
