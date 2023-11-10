import yt_download
from yt_download import AudioYT
import asyncio


async def _get(url):
    return await AudioYT.get_audio(url)


alo = asyncio.run(_get('https://www.youtube.com/watch?v=u_bAWzXkBMo&list=PLL-LXY9dtjAYQ6cK9SbNCbiYml7O11oMt&index=8'))
print(alo.entry['id'])