import datetime
import json
import os

import google.generativeai as palm
import interactions
from interactions import Extension, SlashContext, slash_command

bard = os.getenv("PALM_API_KEY")
palm.configure(api_key=bard)


class Bard(Extension):
    def __init__(self, bot):
        print(">> Lệnh askbard đã sẵn sàng")

    mes = None

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
