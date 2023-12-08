import datetime
import pymysql
import json
import os

from interactions.api.events.discord import MessageCreate
import google.generativeai as palm
import interactions
from interactions import Extension, SlashContext, slash_command, OptionType

bard = os.getenv("PALM_API_KEY")
palm.configure(api_key=bard)


class Bard(Extension):
    db_host = "localhost"
    db_user = "root"
    db_pass = os.getenv("db_password")

    def __init__(self, bot):
        print(bot)
        print(">> Lệnh askbard đã sẵn sàng")

    mes = None

    @interactions.listen()
    async def _bard_mes(self, event: MessageCreate):
        if event.message.author.id == event.bot.user.id:
            return
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database="discord_guild") as connect_thread:
            with connect_thread.cursor() as cursor:
                select_query = (f"SELECT CAST(bard_channel_id AS SIGNED) FROM"
                                f" server_data WHERE ten_server = '{event.message.author.guild.id}'")
                cursor.execute(select_query)
                result = cursor.fetchone()
                if event.message.channel.id != result[0]:
                    return None
                if self.mes is None:
                    self.mes = palm.chat(messages=event.message.content)
                else:
                    self.mes = self.mes.reply(message=event.message.content)
                if self.mes.last is None:
                    self.mes = None
                else:
                    await event.message.channel.send(self.mes.last)

    @slash_command(name="set_bard_channel", description="AI")
    @interactions.slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
    async def set_bard_channel(self, ctx: SlashContext, channel: OptionType.CHANNEL):
        with pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass,
                             database="discord_guild") as connect_thread:
            with connect_thread.cursor() as cursor:
                update_query = (f"UPDATE server_data SET bard_channel_id ="
                                f" '{channel.id}' WHERE ten_server = '{ctx.guild_id}'")
                cursor.execute(update_query)
                connect_thread.commit()
            await ctx.send(channel.id)

    @slash_command(name="askbard", description="Hỏi Palm 1 câu hỏi")
    @interactions.slash_option(
        name="content",
        description="Nội dung câu hỏi",
        opt_type=3,
        required=True,
    )
    async def _askbard(self, ctx: SlashContext, content: str):
        await ctx.defer()
        if self.mes is None:
            self.mes = palm.chat(messages=content)
        else:
            self.mes = self.mes.reply(message=content)
        if self.mes.last is None:
            await self._endbard(ctx)
        else:
            await ctx.send(f'**{ctx.user.display_name}**: {content} \n **bard:** {self.mes.last}')

    @slash_command(name="endbard", description="kết thúc chủ đề")
    async def _endbard(self, ctx: SlashContext):
        now = datetime.datetime.now()
        formatted_t = now.strftime('%Y-%m-%d_%H-%M')
        with open('bardlog/' + formatted_t + '.json', "w") as f:
            json.dump(self.mes.messages, f)
        self.mes = None
        await ctx.send("Đã kết thúc chủ đề")
