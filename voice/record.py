import interactions
from interactions import Extension, File


class Event(Extension):
    @interactions.component_callback("start_recording")
    async def start_recording(self, ctx):
        if not ctx.voice_state:
            vc = ctx.author.voice.channel
            await vc.connect()

        vc = ctx.voice_state
        await vc.start_recording()  # default encoding is `mp3`

        await ctx.send("Bắt đầu Ghi âm!", ephemeral=True)

    @interactions.component_callback("stop_recording")
    async def stop_recording(self, ctx):
        await ctx.defer()
        recorder = ctx.voice_state.recorder
        await recorder.stop_recording()

        await ctx.send(
            "Đã dừng ghi âm",
            files=[
                File(file, file_name=f"ghiam_{user_id}.{recorder.encoding}")
                for user_id, file in recorder.output.items()
            ],
        )

    @interactions.slash_command("record-prompt")
    async def record(self, ctx):
        await ctx.send(
            "Nhấn nút để bắt đầu ghi âm",
            components=[
                interactions.Button(
                    custom_id="start_recording", label="Bắt đầu ghi", style=interactions.ButtonStyle.PRIMARY
                ),
                interactions.Button(
                    custom_id="stop_recording", label="Dừng ghi", style=interactions.ButtonStyle.DANGER
                ),
            ],
        )
