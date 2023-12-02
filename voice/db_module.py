import pymysql
from interactions import Extension, slash_command, slash_option, SlashContext, OptionType


class Database(Extension):
    @slash_command(name="set_record", description="Đặt kênh ghi âm")
    @slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
    async def _record_channel_set(self, ctx: SlashContext, channel: OptionType.CHANNEL):
        with pymysql.connect(host='127.0.0.1', user='root', password='1', database='discord_voice') as connect_thread:
            cursor = connect_thread.cursor()
            update_query = f"UPDATE server_data SET channel_id = '{channel.id}' WHERE guild_id = '{ctx.guild_id}'"
            cursor.execute(update_query)
            connect_thread.commit()
