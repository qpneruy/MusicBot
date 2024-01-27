import logging
import os
from datetime import datetime
import pkgutil
import interactions
from interactions.ext import jurigged

jurigged.watch()
formatted_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
log_filename = f'data/Log/log_{formatted_time}.txt'
log_format = '[%(asctime)s] [%(levelname)s] %(message)s'
date_format = '%H:%M:%S'

# Configure the logger
logger = logging.getLogger('discord_log')
logger.setLevel(logging.DEBUG)
# Configure the file handler
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Configure the stream handler (console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
"""---------------------------------------------------------------------------------"""
api_key = os.getenv('YOUTUBE_API_KEY')
Token = os.getenv("Discord_Token_Bot_A")
"""-----------------------------"""
bot = interactions.Client(
    intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT, send_command_tracebacks=False,
    sync_interactions=True,
    asyncio_debug=True,
    logger=logger)
bot.load_extension("interactions.ext.jurigged")
"""-----------------------------"""


@interactions.listen(interactions.events.Startup)
async def on_start(self):
    print(f">> Bot is Online: {self.bot.user.display_name}")
    # guild = bot.guilds
    # for x in guild:
    #     print(x.name)
    await self.bot.change_presence(status=interactions.Status.IDLE, activity="/help for helpful", )

extension_names = [m.name for m in pkgutil.iter_modules(["Commands"], prefix="Commands.")]
for extension in extension_names:
    bot.load_extension(extension)
extension_names = [m.name for m in pkgutil.iter_modules(["Events"], prefix="Events.")]
for extension in extension_names:
    bot.load_extension(extension)

bot.start(Token)
