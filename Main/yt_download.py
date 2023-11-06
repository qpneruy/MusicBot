import asyncio
from typing import Tuple, Any, Self

import yt_dlp
from yt_dlp import YoutubeDL
from interactions.api.voice.audio import AudioVolume
import json
import string

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
    }
)


class AudioYT(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None
        self._song_url_: []

    @classmethod
    async def get_audio(cls, url: str, ytdl: YoutubeDL | None = None) -> "AudioYT":
        if not ytdl:
            ytdl = cfg_video
        data = await asyncio.to_thread(
            lambda: ytdl.extract_info(url, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        with open('data1.json', "w") as f:
            json.dump(data, f)
        new_cls = cls(data["url"])
        new_cls.ffmpeg_before_args = (
            "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )
        new_cls.entry = data
        return new_cls

    @classmethod
    async def ppl_get(cls, url: str, ytdl: YoutubeDL | None = None) -> list:
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
                __song_list__.insert(0, f'https://www.youtube.com/watch?v={items["id"]}')
        return __song_list__

    @classmethod
    async def ppl_info(cls, url: str, ytdl: YoutubeDL | None = None) -> dict:
        _ppl_inf_: dict = {}
        if not ytdl:
            ytdl = cfg_playlist
        try:
            data = await asyncio.to_thread(
                lambda: ytdl.extract_info(url, download=False)
            )
        except yt_dlp.DownloadError:
            _ppl_inf_["title"] = "The playlist is currently Private"
            _ppl_inf_["availability"] = "private"
            _ppl_inf_["thumbnails"] = "The playlist is currently Private"
            _ppl_inf_["view_count"] = "The playlist is currently Private"
            _ppl_inf_["uploader"] = "The playlist is currently Private"
            _ppl_inf_["playlist_count"] = "The playlist is currently Private"
            return _ppl_inf_
        _ppl_inf_["title"] = data["title"]
        _ppl_inf_["availability"] = data["availability"]
        _ppl_inf_["thumbnails"] = data["thumbnails"][3]["url"]
        _ppl_inf_["view_count"] = data["view_count"]
        _ppl_inf_["uploader"] = data["uploader"]
        _ppl_inf_["playlist_count"] = data["playlist_count"]
        return _ppl_inf_


class YTAudio(AudioVolume):
    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.entry: dict | None = None

    @classmethod
    async def from_url(
            cls, url: str, stream: bool = True, ytdl: YoutubeDL | None = None) -> Self:
        if not ytdl:
            ytdl = youtube_dl
        data = await asyncio.to_thread(
            lambda: ytdl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            data = data["entries"][0]
        filename = data["url"] if stream else ytdl.prepare_filename(data)
        new_cls = cls(filename)
        if stream:
            new_cls.ffmpeg_before_args = (
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            )
        new_cls.entry = data
        return new_cls