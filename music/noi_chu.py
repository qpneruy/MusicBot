import json

import aiohttp
import interactions
from interactions import Extension, slash_command, SlashContext, OptionType, slash_option
from interactions.api.events import MessageCreate


class NoiChu(Extension):
    def __init__(self, bot):
        print(bot)
        print(">> Game Nối chữ đã sẵn sàng")

    model_data = {
        "channel_id": "None",
        "history": {
            "word_list": [],
            "previous_user": "None",
        },
        "current": "None",
    }

    @slash_command(name="reset_noi_chu", description="Xóa dữ liệu")
    async def _reset(self, ctx: SlashContext):

        with open(f"json/word_data_sv_{ctx.guild.id}", "w") as datafile:
            json.dump(self.model_data, datafile, indent=4)
        await ctx.send(f"↩️ Đã reset nối chữ")

    @slash_command(name="word_setup", description="Đặt kênh nối chữ")
    @slash_option(name="channel", description="Chọn kênh", opt_type=OptionType.CHANNEL, required=True)
    async def _world_setup(self, ctx: SlashContext, channel: OptionType.CHANNEL):
        with open(f'json/word_data_sv_{ctx.guild.id}', 'w') as f:
            self.model_data["channel_id"] = f"{channel.id}"
            json.dump(self.model_data, f, indent=4)
        await ctx.send(f'Đã Đặt kênh {channel.name} thành kênh nối chữ')
        ctx = channel
        await ctx.send('✅ Bắt đầu chơi')

    @interactions.listen()
    async def on_message(self, event: MessageCreate):
        try:
            guild_id = event.message.author.guild.id
        except AttributeError:
            return
        try:
            open(f"json/word_data_sv_{guild_id}", "r")
        except FileNotFoundError:
            return
        with open(f"json/word_data_sv_{guild_id}", "r") as f:
            temp_data = json.load(f)
        if not str(event.message.channel.id) == temp_data["channel_id"]:
            return
        if temp_data["channel_id"] != str(event.message.channel.id):
            return
        if event.message.author.id == event.bot.user.id:
            return
        async with aiohttp.ClientSession() as session:
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
            if data["history"]["previous_user"] == event.message.author.id:
                await event.message.channel.send("Bạn đã nối từ trước đó rồi")
                await event.message.add_reaction('❌')
                return
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
