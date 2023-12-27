import pymysql

import interactions
from interactions import listen, slash_command, slash_option, SlashContext, OptionType
from interactions.api.events import VoiceUserJoin, VoiceUserLeave


class ChannelListen(interactions.Extension):
    @classmethod
    async def get_remaining_members(cls, current_channel) -> int:
        members = await current_channel.fetch_members()
        total_members = len(members)
        return total_members

    @listen(VoiceUserJoin)
    async def __join(self, vs: VoiceUserJoin):
        with pymysql.connect(host='127.0.0.1', user='root', password='W2:)G8%ZLj~8#',
                             database='discord_guild') as connect_thread:
            with connect_thread.cursor() as cursor:
                select_query = f"SELECT CAST(voice_id AS SIGNED) FROM server_data WHERE ten_server = '{vs.author.guild.id}'"
                cursor.execute(select_query)
                result = cursor.fetchone()
                if not result:
                    return
                if vs.channel.id == result[0]:
                    channel_d = await vs.channel.category.create_voice_channel(f"{vs.author.display_name} Channel")
                    channel_id = channel_d.id
                    channel_d.user_limit = 10
                    await channel_d.edit(user_limit=5)
                    query = f"INSERT INTO server_{vs.author.guild.id}(active_channel) VALUES ({channel_id}) "
                    cursor.execute(query)
                    connect_thread.commit()
                    mem = vs.author
                    await mem.move(channel_d.id)

    @listen(VoiceUserLeave)
    async def __leave(self, vs: VoiceUserLeave):
        with pymysql.connect(host='127.0.0.1', user='root', password='W2:)G8%ZLj~8#',
                             database='discord_guild') as connect_thread:
            if len(vs.channel.voice_members) >= 2:
                return
            with connect_thread.cursor() as cnx:
                query = f"SELECT CAST(active_channel AS SIGNED) FROM server_{vs.author.guild.id}"
                cnx.execute(query)
                res = cnx.fetchall()
                res_values = [item[0] for item in res]
                if vs.channel.id in res_values:
                    await vs.channel.delete()
                query = f"DELETE FROM server_{vs.author.guild.id} WHERE active_channel = {vs.channel.id}"
                cnx.execute(query)
                connect_thread.commit()

    @slash_command(name="set_voice", description="Voice create channel set")
    @slash_option(name="channel", description="Channel select", opt_type=OptionType.CHANNEL, required=True)
    async def _setup(self, ctx: SlashContext, channel: interactions.OptionType.CHANNEL):
        with pymysql.connect(host='127.0.0.1', user='root', password='W2:)G8%ZLj~8#',
                             database='discord_guild') as connect_thread:
            channels = channel.id
            await ctx.send(f"set {channel.name} successful")
            with connect_thread.cursor() as cursor:
                update_query = f"UPDATE server_data SET voice_id = '{channels}' WHERE ten_server = '{ctx.guild_id}'"
                cursor.execute(update_query)
                connect_thread.commit()
                print(f"value of voice_id is successful set {ctx.guild_id}.")
