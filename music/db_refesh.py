import os

import interactions
import pymysql
from interactions import Extension, slash_command, SlashContext
from interactions.api.events.base import GuildEvent


# Kiễm tra xem bảng có tồn tại trong database không
def table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None


def get_all_tables(cursor, database_name):
    cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{database_name}'")
    return [table[0] for table in cursor.fetchall()]


class Database(Extension):
    db_host = "localhost"
    db_user = "root"
    db_pass = os.getenv("db_password")
    password = os.getenv("db_password")

    @interactions.listen()
    async def _on_guild_join(self, guild: GuildEvent):
        """create guild data from database"""
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_guild') as connect_thread:
            with connect_thread.cursor() as cursor:
                query = f"CREATE TABLE server_{guild.guild_id}(active_channel VARCHAR(255) not NULL)"
                cursor.execute(query)
                new_data = {
                    'ten_server': guild.guild_id,
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
                connect_thread.commit()
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_voice') as connect_thread:
            with connect_thread.cursor() as cursor:
                new_data = {
                    'guild_id': guild.guild_id,
                    'channel_id': 'NULL',
                    'record_state': 'NULL',
                }
                insert_data_query = """
                                INSERT INTO server_data (guild_id, channel_id, record_state)
                                VALUES (%(guild_id)s, %(channel_id)s, %(record_state)s)
                                """
                cursor.execute(insert_data_query, new_data)
                connect_thread.commit()

    @interactions.listen()
    async def _on_guild_left(self, Guild: GuildEvent):
        """delete guild data from database"""
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_guild') as connect_thread:
            with connect_thread.cursor() as cursor:
                drop_query = f"DROP TABLE 'server_{Guild.guild_id}'"
                cursor.execute(drop_query)
                delete_query = f"DELETE FROM server_data WHERE ten_server = {Guild.guild_id} "
                cursor.execute(delete_query)
        connect_thread.commit()
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_voice') as connect_thread:
            with connect_thread.cursor() as cursor:
                delete_query = f"DELETE FROM server_data WHERE guild_id = {Guild.guild_id} "
                cursor.execute(delete_query)
        connect_thread.commit()

    # async def _insert_if_not_exists(self, ) -> bool:
    #     """Check the value if not exits in table then add it to the table"""
    #     with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass) as connect_thread:
    #         with connect_thread.cursor() as cursor:
    #             Check_query = """
    #             IF NOT EXITS
    #             """

    # @slash_command(name='db_refreshv1', description="Làm mới cơ sở dữ liệu (tạo)")
    # async def dbv1_command(self, ctx: SlashContext):
    #     guilds = ctx.bot.guilds
    #     connection = pymysql.connect(host=self.host, user='root', password=self.password, database='discord_guild')
    #     create_table_query = """
    #         CREATE TABLE IF NOT EXISTS server_data (
    #             ten_server VARCHAR(255) NOT NULL,
    #             voice_id VARCHAR(255) NOT NULL,
    #             gpt_channel_id VARCHAR(255) NOT NULL,
    #             bard_channel_id VARCHAR(255) NOT NULL,
    #             current_vol DOUBLE NOT NULL
    #         )
    #     """
    #     cursor = connection.cursor()
    #     cursor.execute(create_table_query)
    #     for guild in guilds:
    #         if not table_exists(cursor, f'server_{guild.id}'):
    #             query = f"CREATE TABLE server_{guild.id}(active_channel VARCHAR(255) not NULL)"
    #             cursor.execute(query)
    #         select_query = f"SELECT * FROM server_data WHERE ten_server = {guild.id}"
    #         cursor.execute(select_query)
    #         result = cursor.fetchall()
    #         if result:
    #             print(f"Giá trị {guild.id} tồn tại trong cột 'ten_server'.")
    #         else:
    #             print(f"Giá trị {guild.id} đã được thêm.")
    #             new_data = {
    #                 'ten_server': guild.id,
    #                 'voice_id': 'NULL',
    #                 'gpt_channel_id': 'NULL',
    #                 'bard_channel_id': 'NULL',
    #                 'current_vol': 0.5
    #             }
    #             insert_data_query = """
    #             INSERT INTO server_data (ten_server, voice_id, gpt_channel_id, bard_channel_id, current_vol)
    #             VALUES (%(ten_server)s, %(voice_id)s, %(gpt_channel_id)s, %(bard_channel_id)s, %(current_vol)s)
    #             """
    #             cursor.execute(insert_data_query, new_data)
    #     connection.commit()
    #     connection.close()
    #     with pymysql.connect(host='127.0.0.1', user='root', password='W2:)G8%ZLj~8#',
    #                          database='discord_voice') as connect_thread:
    #         cursor = connect_thread.cursor()
    #         guilds = ctx.bot.guilds
    #         for guild in guilds:
    #             select_query = f"SELECT * FROM server_data WHERE guild_id = {guild.id}"
    #             cursor.execute(select_query)
    #             result = cursor.fetchall()
    #             print('>>>>>>>>>>', result)
    #             if result:
    #                 print(f"Giá trị {guild.id} tồn tại trong cột 'ten_server'.")
    #             else:
    #                 print(f"Giá trị {guild.id} đã được thêm.")
    #                 insert_data_query = """
    #                     INSERT INTO server_data (guild_id, record_state)
    #                     VALUES (%(guild_id)s, %(record_state)s)
    #                     """
    #                 cursor.execute(insert_data_query, {'guild_id': guild.id, 'record_state': False})
    #             cursor.execute(select_query)
    #         connect_thread.commit()
    #     await ctx.send('Đã làm mới cơ sở dữ liệu phương thức tạo')
