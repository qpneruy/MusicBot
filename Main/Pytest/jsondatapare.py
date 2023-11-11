import json

import yt_download
from yt_download import AudioYT
import asyncio


async def _get(url):
    return await AudioYT.ppl_get(url)


alo = asyncio.run(_get('https://www.youtube.com/playlist?list=PLL-LXY9dtjAZQR-pNpulzqdz20houyw-0'))
print(alo)