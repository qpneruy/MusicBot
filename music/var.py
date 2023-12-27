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
        "skip_download": True
    }
)

list_url = []

d = 0


def _get_song_info(url: str):
    try:
        data = cfg_video.extract_info(url, download=False)
        with open(f"data9999.json", "w") as f:
            json.dump(data["duration"], f, indent=4)
        return data
    except yt_dlp.utils.DownloadError:
        return None


data = cfg_playlist.extract_info(url='https://www.youtube.com/playlist?list=PLL-LXY9dtjAaATMLXJlsLWMN-YplTdLU4',
                                 download=False)

with ThreadPoolExecutor(max_workers=6) as executor:
    data_music = executor.map(lambda urld: _get_song_info(urld["url"]),
                              data["entries"])
i = 0
for items in data_music:
    i += 1
    with open(f"data{i}.json", "w") as f:
        json.dump(items, f, indent=4)