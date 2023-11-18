import interactions
from interactions import Extension, SlashContext, slash_command
import openai
import os


class Gpt(Extension):
    def __init__(self, bot):
        print(">> Lệnh askgpt đã sẵn sàng")
    gpt = os.getenv("OPENAI_API_KEY")
    openai.api_key = gpt

    @slash_command(name="askgpt", description="Hỏi gpt 1 câu hỏi")
    @interactions.slash_option(
        name="content",
        description="nội dung câu hỏi",
        opt_type=3,
        required=True
    )
    async def _askgpt(self, ctx: SlashContext, content: str):
        # logger.debug(f"[{ctx.guild.name}]::[{ctx.user.display_name}]: > ASKGPT: {content}")
        await ctx.defer()
        if len(content) <= 2000:
            message = content
            if message:
                messages.append(
                    {"role": "user", "content": message},
                )
                chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages
                )
                reply = chat.choices[0].message.content
                if len(reply) > 2000:
                    await ctx.send('câu trả lời quá dài vui lòng hỏi câu hác :))')
                else:
                    await ctx.send(
                        f'**{ctx.user.display_name}:** {content}\n**qpneruy:** {reply}')

                messages.append({"role": "assistant", "content": reply})
        else:
            await ctx.send("tin nhắn quá 2000 ký tự", ephemeral=True)

    @slash_command(name='img', description="Tạo ảnh theo mô tả")
    @interactions.slash_option("prompt", "mô tả ảnh", 3, True)
    async def _img(self, ctx: SlashContext, prompt: str):
        await ctx.defer()
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024X1024"
        )
        image_url = response['data'][0]['url']
        await ctx.send(image_url)
