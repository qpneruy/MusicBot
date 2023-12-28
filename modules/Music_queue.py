import asyncio
from collections import deque
from typing import Iterator

from interactions import ActiveVoiceState, Embed, ButtonStyle, ActionRow, Button
from interactions.api.voice.audio import BaseAudio
from modules import YT_Downloader
import os
import string

import requests
from yt_dlp import YoutubeDL


class VideoData:
    def __init__(self):
        self.tokenA = os.getenv('YOUTUBE_API_KEY_1')
        self.tokenB = os.getenv('YOUTUBE_API_KEY_2')
        self.api_key = self.tokenA
    youtube_dl = YoutubeDL(
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

    async def get_uploader_avt(self, url: str | None = None, direct_url: any = None) -> str:
        if direct_url is not None:
            data = direct_url
        else:
            data = self.youtube_dl.extract_info(url, download=False)
        channel_id = data['channel_id']
        print(channel_id)
        channel_url = f'https://www.googleapis.com/youtube/v3/channels?key={self.api_key}&part=snippet&id={channel_id}'
        channel_response = requests.get(channel_url)
        if channel_response.status_code == 200:
            channel_data = channel_response.json()
            avatar_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
            return avatar_url


class MusicQueue:
    voice_state: ActiveVoiceState
    _entries: deque
    _item_queued_: asyncio.Event
    _last_audio: BaseAudio
    VideoData = VideoData()

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self.__song_list__ = []
        self._item_queued = asyncio.Event()
        self.task = asyncio.Task
        self.loop_state = False
        self.last_audio = BaseAudio
        self.destroy_queue = False

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    async def data_process(self, url_list: deque | str, playlist: bool) -> None:
        GuildMusicMN = GuildMusicManager()
        Youtube_DL = GuildMusicMN.get_dl(self.voice_state.guild.id)
        if playlist:
            while not self.destroy_queue:
                if len(url_list) == 0:
                    self.destroy_queue = True
                while len(url_list) > 0:
                    url = url_list.pop()
                    audio = await Youtube_DL.get_audio(url)
                    print(audio)
                    avatar_url = await self.VideoData.get_uploader_avt(f'https://www.youtube.com/watch?v={audio.entry["id"]}')
                    self.put(audio, avatar_url)
        else:
            audio = await Youtube_DL.get_audio(url_list)
            avatar_url = await self.VideoData.get_uploader_avt(f'https://www.youtube.com/watch?v={audio.entry["id"]}')
            self.put(audio, avatar_url)

    def put(self, audio_d, avatar_url: str) -> None:
        title = audio_d.entry['title']
        thumbnail = audio_d.entry['thumbnail']
        uploader = audio_d.entry['uploader']
        duration = audio_d.entry['duration']
        embed = Embed(
            title=f" {title}",
            description="ㅤ",
            color=0x5f9afa,
        )
        duration_hms = convert_seconds_to_hms(duration)
        embed.set_image(thumbnail)
        embed.add_field(name="Upload By:  ", value=f"{uploader}", inline=True)
        embed.add_field(name=" Duration:  ", value=f"{duration_hms}", inline=True)
        embed.set_thumbnail(url=avatar_url)
        nut = ActionRow(
            Button(
                style=ButtonStyle.LINK,
                label="Link",
                url=f'https://www.youtube.com/watch?v={audio_d.entry["id"]}'
            ),
            Button(
                custom_id="skip_button",
                style=ButtonStyle.GREY,
                label="⏭️ Skip",
            )
        )
        self.__song_list__.insert(0, [embed, nut])
        self._entries.append(audio_d)
        self._item_queued.set()

    def get_list(self) -> deque:
        return self._entries

    def put_first(self, audio_d: BaseAudio) -> None:
        self._entries.appendleft(audio_d)
        self._item_queued.set()

    async def pop(self) -> BaseAudio:
        if len(self) == 0:
            await self._item_queued.wait()
        item = self._entries.popleft()
        self._item_queued.clear()
        return item

    def pop_no_wait(self) -> BaseAudio:
        return self._entries.popleft()

    def shuffle(self) -> None:
        print('alo')

    def clear(self) -> None:
        self._entries.clear()

    def peek(self, positions: int = 1) -> BaseAudio | None:
        try:
            return self._entries[positions - 1]
        except IndexError:
            return None

    def loop(self) -> None:
        if self.loop_state is True:
            self.loop_state = False
        else:
            self.loop_state = True
        print("Trang thai: ", self.loop_state)

    def peek_at_index(self, index: int) -> BaseAudio:
        return self._entries[index]

    def peek_at_index_no_wait(self, index: int) -> BaseAudio:
        return self._entries[index]

    async def __playback_queue(self) -> None:
        while self.voice_state.connected:
            print("Running 1")
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            audio_d = await self.pop()
            _song_msg_ = self.__song_list__.pop()
            _song_msg_[0].set_author('💿 Playing')
            await self.voice_state.channel.send(embed=_song_msg_[0])
            await self.voice_state.channel.send(components=_song_msg_[1], silent=True)

            await self.voice_state.play(audio_d)

    async def stop(self) -> None:
        await self.voice_state.stop()

    async def resume(self) -> None:
        self.voice_state.resume()

    async def pause(self) -> None:
        self.voice_state.pause()

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        self.task = asyncio.create_task(self())


# Chuẩn hóa thời lượng
def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"


# Quản lý các lớp NaffQueue thuộc mỗi ctx.guild.id
class GuildMusicManager:
    _queues_ = {}
    _music_dl_ = {}

    def get_queue(self, server_id, voice_state: ActiveVoiceState):
        if server_id not in self._queues_:
            self._queues_[server_id] = MusicQueue(voice_state)
        return self._queues_[server_id]

    def get_dl(self, server_id):
        if server_id not in self._music_dl_:
            self._music_dl_[server_id] = YT_Downloader.YTDownloader
        return self._music_dl_[server_id]
