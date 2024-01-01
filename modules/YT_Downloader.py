import asyncio
import yt_dlp
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
        "skip_download": True
    }
)
cfg_playlist = YoutubeDL(
    {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": False,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        "extract_flat": True,
        "dump_single_json": True,
        "skip_download": True
    }
)


class YTDownloader(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None

    @classmethod
    async def get_audio(cls, url: str) -> "YTDownloader" or None:
        print('>>>', url)
        try:
            data = await asyncio.to_thread(
                lambda: cfg_video.extract_info(url, download=False)
            )
        except yt_dlp.utils.DownloadError:
            return None
        if "entries" in data:
            data = data["entries"][0]
        new_cls = cls(data["url"])
        new_cls.ffmpeg_before_args = (
            "-reconnect 0 -reconnect_streamed 0 -reconnect_delay_max 10"
        )
        new_cls.entry = data
        return new_cls

    @classmethod
    async def extra_info(cls, url: str):
        try:
            data = await asyncio.to_thread(
                lambda: cfg_playlist.extract_info(url, download=False)
            )
            return data
        except yt_dlp.utils.DownloadError:
            return None

    @classmethod
    def create_new_cls(cls, entry_data):
        new_cls = cls(entry_data['url'])
        new_cls.ffmpeg_before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        new_cls.entry = entry_data
        return new_cls
