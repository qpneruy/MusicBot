from collections import deque
import yt_dlp
from modules import YTDownloader
import asyncio

process_queue = deque()
url_d = "https://www.youtube.com/playlist?list=PLL-LXY9dtjAY21uETLQS_QUWcNcNHpsTA"
downloader = YTDownloader(url_d)
data = downloader.links_get(url_d)
for item in data["entries"]:
    process_queue.insert(0, item["url"])


playback_queue = deque()


def peak():
    global process_queue
    try:
        return process_queue[0]
    except IndexError:
        return None


async def playback_queue__():
    while True:
        if peak() is not None:
            url = process_queue.pop()
            audio_d = await downloader.get_audio(url)
            print(audio_d.entry["title"])
            playback_queue.insert(0, audio_d)
asyncio.run(playback_queue__())

