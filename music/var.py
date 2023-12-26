import yt_dlp
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

cfg_playlist = yt_dlp.YoutubeDL(
    {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": False,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        "extract_flat": True,
        # 'dumpjson': True,
        "dump_single_json": True,
        "skip_download": True
    }
)
cfg_video = yt_dlp.YoutubeDL(
    {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
    }
)

list_url = []

d = 0


def get_audio(url1: str):
    global d
    # print('>>', url1)
    data_d = cfg_video.extract_info('https://www.youtube.com/watch?v=wm28LQVh9-o', download=False)
    d += 1
    print(d)
    return data_d


result = cfg_playlist.extract_info(url='https://www.youtube.com/playlist?list=PLL-LXY9dtjAaATMLXJlsLWMN-YplTdLU4',
                                   download=False)

with ThreadPoolExecutor() as executor:
    data = executor.map(lambda urld: print(urld["url"]), result["entries"])
# for val in data:
#     print(val["url"])
data_d = cfg_video.extract_info('https://www.youtube.com/watch?v=wm28LQVh9-o', download=False)
print(data_d)