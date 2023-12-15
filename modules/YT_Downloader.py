import asyncio

import yt_dlp
from interactions.api.voice.audio import AudioVolume
from concurrent.futures import ThreadPoolExecutor
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
        # "extract_flat": True,
        # 'dumpjson': True,
        "dump_single_json": True,
        "skip_download": True
    }
)


class YTDownloader(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None
        self._song_url_: []

    @classmethod
    def get_audio(cls, url: str, ytdl: YoutubeDL | None = None) -> "YTDownloader":
        if not ytdl:
            ytdl = cfg_video
        # data = await asyncio.to_thread(
        #     lambda: ytdl.extract_info(url, download=False)
        # )
        # with ThreadPoolExecutor() as executor:
        #     loop = asyncio.get_event_loop()
        data = ytdl.extract_info(url, download=False)
        # if "entries" in data:
        #     data = data["entries"][0]
        # new_cls = cls(data["url"])
        # new_cls.ffmpeg_before_args = (
        #     "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        # )
        # new_cls.entry = data
        # return new_cls
        print(data["title"])
        return data

    @classmethod
    async def get_extra_info_async(cls, url: str):
        data = await asyncio.to_thread(
            lambda: cfg_playlist.extract_info(url, download=False)
        )
        return data

    # Không sử dụng
    @classmethod
    async def ppl_get(cls, url: str | None = None, ytdl: YoutubeDL | None = None) -> list:
        __song_list__: [] = []
        if not ytdl:
            ytdl = cfg_playlist
        try:
            data = await asyncio.to_thread(
                lambda: ytdl.extract_info(url, download=False)
            )
        except yt_dlp.DownloadError:
            return []
        if "entries" in data:
            for items in data["entries"]:
                items = cls.create_new_cls(items)
                __song_list__.insert(0, items)

        return __song_list__

    # Không sử dụng
    @classmethod
    async def from_url(cls, url: str) -> "YTDownloader":
        data = await asyncio.to_thread(
            lambda: cfg_video.extract_info(url, download=False)
        )
        new_cls = cls(data)
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

    @classmethod
    async def ppl_info(cls, url: str | None = None, direct_data: dict = None, ytdl: YoutubeDL | None = None) -> dict:
        _ppl_inf_: dict = {}
        if direct_data is not None:
            data = direct_data
        else:
            if ytdl is None:
                ytdl = cfg_playlist
            try:
                data = await asyncio.to_thread(
                    lambda: ytdl.extract_info(url, download=False)
                )
            except yt_dlp.DownloadError or TypeError:
                _ppl_inf_["title"] = "The playlist is currently Private"
                _ppl_inf_["availability"] = "private"
                _ppl_inf_["thumbnails"] = "The playlist is currently Private"
                _ppl_inf_["view_count"] = "The playlist is currently Private"
                _ppl_inf_["uploader"] = "The playlist is currently Private"
                _ppl_inf_["playlist_count"] = "The playlist is currently Private"
                return _ppl_inf_
        try:
            return data
        except Exception as e:
            print(f"Error: {e}")
            return {}
