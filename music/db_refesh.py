import os

import interactions
import pymysql
from interactions import Extension
from interactions.api.events import GuildJoin, GuildLeft


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

    @interactions.listen(GuildJoin)
    async def _on_guild_join(self, guild: GuildJoin):
        """create guild data from database"""
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_guild') as connect_thread:
            with connect_thread.cursor() as cursor:
                query = f"CREATE TABLE server_{guild.guild_id}(active_channel VARCHAR(255) not NULL)"
                try:
                    cursor.execute(query)
                except pymysql.err.OperationalError:
                    print(f"Bảng {guild.guild_id} đã tồn tại")
                    return
                new_data = {
                    'ten_server': guild.guild_id,
                    'voice_id': 'NULL',
                    'gpt_channel_id': 'NULL',
                    'bard_channel_id': 'NULL',
                    'current_vol': 0.5
                }
                insert_data_query = """
                                INSERT INTO server_data (ten_server, voice_id, gpt_channel_id,
                                 bard_channel_id, current_vol)
                                VALUES (%(ten_server)s, %(voice_id)s, %(gpt_channel_id)s, 
                                %(bard_channel_id)s, %(current_vol)s)
                                """
                cursor.execute(insert_data_query, new_data)
                connect_thread.commit()
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_voice') as connect_thread:
            with connect_thread.cursor() as cursor:
                new_data = {
                    'guild_id': guild.guild_id,
                }
                insert_data_query = """
                                INSERT INTO server_data (guild_id)
                                VALUES (%(guild_id)s)
                                """
                cursor.execute(insert_data_query, new_data)
                connect_thread.commit()

    @interactions.listen(GuildLeft)
    async def _on_guild_left(self, Guild: GuildLeft):
        """delete guild data from database"""
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database='discord_guild') as connect_thread:
            with connect_thread.cursor() as cursor:
                drop_query = f"DROP TABLE server_{Guild.guild_id}"
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
