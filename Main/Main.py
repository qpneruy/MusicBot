import os
import datetime as dt
import interactions
from interactions import SlashContext, ActionRow, Button, ButtonStyle, slash_command, StringSelectMenu, Embed, slash_option, OptionType
from interactions.api.events import Component

Token = os.getenv("Discord_Token_bot")
bot = interactions.Client();
startup = dt.datetime.utcnow()
@slash_command(name="help", description="Trợ Giúp")
async def _help(ctx: SlashContext):
    embed = Embed(
        title="**Giúp Đỡ**                       ",
        description="  ",
        color=0x6DAEDB,
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="**📖️ ╏ COMMAND**", value='ㅤ  /about -- Trạng thái bot\nㅤ /Spam -- Spam @ everyone \nㅤ  /channel_Nuke -- Nuke server bằng kênh đồng thời tag everyone')
    await ctx.send(embed=embed)
@slash_command(name="about", description="Trạng Thái Bot")
async def _about(ctx: SlashContext):
    embed2 = Embed(
        title="BOT STATUS",
        description="ㅤ",
        color=0x00ff00,
    )

    cacl = dt.datetime.utcnow();
    embed2.add_field(name="🌐PING", value= f"{round(bot.latency*1000)} msㅤㅤㅤㅤㅤ", inline=True )
    embed2.add_field(name="🟢UPTIME",value=f"{cacl-startup}", inline=True)
    await ctx.send(embeds=embed2)
@slash_command(name="channel_nuke", description="Nuke dis bằng channel", options=
[
    {
    "name": "n",
    "description": "Số  Lượng kênh",
    "type": OptionType.INTEGER,
    "required": True,
    },
    {
    "name": "type_c",
    "description": "Loai Kenh 0 chat 2 voice",
    "type": OptionType.INTEGER,
    "required": True,
    }
]
)
async def _nuke_channel(ctx: SlashContext, n: int, type_c: int):
    for i in range(1, n):
      channel = await ctx.guild.create_channel(type_c, str(i) )
      await channel.send('@everyone')
bot.start(Token)