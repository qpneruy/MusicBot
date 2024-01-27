import asyncio
import json

from interactions.api.voice.audio import AudioVolume
from yt_dlp import YoutubeDL

cfg_video = YoutubeDL(
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
        # "extract_flat": True,
        "dump_single_json": True,
        # 'dumpjson': True,
        "skip_download": True,
        "concurrent-fragments": 4
    }
)


class YTDownloader(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None

    @classmethod
    async def get_audio(cls, url: str, ytdl: YoutubeDL | None = None) -> "YTDownloader":
        if not ytdl:
            ytdl = cfg_video
        data = await asyncio.to_thread(
            lambda: ytdl.extract_info(url, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        new_cls = cls(data["original_url"])
        new_cls.ffmpeg_before_args = (
            "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        new_cls.entry = data
        return new_cls

    @classmethod
    def create_new_cls(cls, entry_data):
        new_cls = cls(entry_data['url'])
        new_cls.ffmpeg_before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 7"
        new_cls.entry = entry_data
        return new_cls
