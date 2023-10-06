import interactions
import os
token = os.getenv("Discord_token_bot_B")
client = interactions.Client(token=token)

@client.command(
    name="ping",
    description="Ping pong",
)
async def _ping(ctx: interactions.CommandContext):
    await ctx.send("Pong!")

@client.event
async def on_ready():
    print("Ready!")

client.start()