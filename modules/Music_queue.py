import asyncio
import json
from collections import deque
from typing import Iterator, Any

import yt_dlp.utils
from interactions import ActiveVoiceState, Embed, ButtonStyle, ActionRow, Button
from interactions.api.voice.audio import BaseAudio, AudioVolume
from modules import YT_Downloader
import os

import requests
from yt_dlp import YoutubeDL
import os


class VideoData:
    def __init__(self):
        # Get the first YouTube API key from the environment variables
        self.tokenA = os.getenv('YOUTUBE_API_KEY_1')
        # Get the second YouTube API key from the environment variables
        self.tokenB = os.getenv('YOUTUBE_API_KEY_2')
        # Set the initial API key to the first YouTube API key
        self.api_key = self.tokenB

    youtube_dl = YoutubeDL(
        {
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
        }
    )

    async def get_uploader_avt(self, url: str | None = None, direct_url: any = None) -> str:
        """
        Retrieves the uploader's avatar URL from a given YouTube video URL or direct URL.

        Args:
            url (str | None): The YouTube video URL.
            direct_url (any): Direct URL to retrieve the uploader's avatar from.

        Returns:
            url (str): The URL of the uploader's avatar.
            dirict_url (any): Direct URL to retrieve the uploader's avatar from.
        """
        if direct_url is not None:
            data = direct_url
        else:
            data = self.youtube_dl.extract_info(url, download=False)

        channel_id = data['channel_id']
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
    VideoData = VideoData()
    _curent_queue_index: int

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self.__song_list__ = []
        self._item_queued = asyncio.Event()
        self.destroy_queue = False
        self._curent_queue_index = -1
        self.title_list = []

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    async def data_process(self, url_list: list | str, playlist: bool) -> None:
        """
        Process the given list of URLs and add the audio and avatar URL to the queue.

        Args:
            url_list (list | str): A deque or string representing the list of URLs.
            playlist (bool): A boolean indicating whether the given URLs are part of a playlist.
        """
        # Process URLs in playlist mode
        if playlist:
            while not self.destroy_queue:
                if len(url_list) == 0:
                    self.destroy_queue = True
                while len(url_list) > 0:
                    url = url_list.pop()
                    audio = await YT_Downloader.YTDownloader.get_audio(url)
                    if audio is not None:
                        avatar_url = await self.VideoData.get_uploader_avt(url)
                        self.put(audio, avatar_url)
        # Process single URL
        else:
            audio = await YT_Downloader.YTDownloader.get_audio(url_list)
            avatar_url = await self.VideoData.get_uploader_avt(f'https://www.youtube.com/watch?v={audio.entry["id"]}')
            self.put(audio, avatar_url)

    def put(self, audio_d, avatar_url: str) -> None:
        # Get the title, thumbnail, uploader, and duration from the audio_d entry
        title = audio_d.entry['title']
        self.title_list.append(title)
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

        self.__song_list__.append([embed, nut])
        self._entries.append(AudioVolume(audio_d.entry["url"]))
        self._item_queued.set()

    def get_list(self) -> deque:
        return self._entries

    def get_title_list(self) -> list:
        return self.title_list

    def clear(self) -> None:
        self._entries.clear()

    def peek(self) -> BaseAudio | None:
        try:
            return self._entries[self._curent_queue_index]
        except IndexError:
            return None

    def peek_at_index(self, index: int) -> Any | None:
        try:
            return self._entries[index]
        except IndexError:
            return None

    async def pop(self) -> BaseAudio:
        if len(self) == 0:
            await self._item_queued.wait()
        self._curent_queue_index += 1
        item = self._entries[self._curent_queue_index]
        self._item_queued.clear()
        return item

    async def __playback_queue(self) -> None:
        """
      This function manages the playback queue for the voice bot.
      It plays audio tracks from the queue one by one until the voice state is disconnected.
      """

        while self.voice_state.connected:
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            if len(self._entries) == 0 or self.peek_at_index(self._curent_queue_index) is None:
                await self._item_queued.wait()
            print("Current index:", self._curent_queue_index)
            audio_d = await self.pop()

            _song_msg_ = self.__song_list__[self._curent_queue_index]
            _song_msg_[0].set_author('💿 Playing')
            await self.voice_state.channel.send(embed=_song_msg_[0])
            await self.voice_state.channel.send(components=_song_msg_[1], silent=True)

            await self.voice_state.play(audio_d)

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        asyncio.create_task(self())

    async def skipto(self, index: int) -> None:
        self._curent_queue_index = index - 1
        await self.__stop()

    async def __stop(self) -> None:
        await self.voice_state.stop()

    def destroy(self) -> None:
        self._entries.clear()
        self._item_queued.clear()
        self._curent_queue_index = 0


# Chuẩn hóa thời lượng
def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"


# Quản lý các lớp Music queue thuộc mỗi ctx.guild.id
class GuildMusicManager:
    _queues_ = {}

    def get_queue(self, server_id, voice_state: ActiveVoiceState):
        """
      Get the music queue for a specific server.

      Args:
          server_id (str): The ID of the server.
          voice_state (ActiveVoiceState): The voice state of the server.

      Returns:
          MusicQueue: The music queue for the server.
      """
        if server_id not in self._queues_:
            self._queues_[server_id] = MusicQueue(voice_state)
        return self._queues_[server_id]
