import asyncio
import random
from collections import deque
from typing import Iterator
from interactions import ActiveVoiceState, Embed, SlashContext, ButtonStyle, ActionRow, Button
from interactions.api.voice.audio import BaseAudio


class NaffQueue:
    voice_state: ActiveVoiceState
    _entries: deque
    _item_queued: asyncio.Event
    loopstate: bool
    last: None

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self._item_queued = asyncio.Event()
        self.__song_list__ = []
        self.__song_link__ = []
        self._current_task = None
        self.loopstate = False

    def __len__(self) -> int:
        return len(self._entries)

    def loops(self) -> None:
        if not self.loopstate:
            self.loopstate = True
        elif self.loopstate:
            self.loopstate = False

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    def put(self, audio_d: BaseAudio, avatar_url: str) -> None:
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
        embed.add_field(name="Tải lên bởi:  ", value=f"{uploader}", inline=True)
        embed.add_field(name=" Dài:  ", value=f"{duration_hms}", inline=True)
        embed.set_thumbnail(url=avatar_url)
        nut = Button(
            style=ButtonStyle.LINK,
            label="Link",
            url=f'https://www.youtube.com/watch?v={audio_d.entry["id"]}'
        )
        self.__song_link__.insert(0, nut)
        self.__song_list__.insert(0, embed)
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
        random.shuffle(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def peek(self, positions: int = 1) -> BaseAudio | None:
        try:
            return self._entries[positions - 1]
        except IndexError:
            return None

    def peek_at_index(self, index: int) -> BaseAudio:
        return self._entries[index]

    async def __playback_queue(self) -> None:
        while self.voice_state.connected:
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            audio_d = await self.pop()
            embed = self.__song_list__.pop()
            embed.set_author('💿 Đang chơi')
            nut = self.__song_link__.pop()
            await self.voice_state.channel.send(embed=embed)
            await self.voice_state.channel.send(components=nut)
            await self.voice_state.play(audio_d)

    async def _stop(self) -> None:
        await self.voice_state.stop()

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        asyncio.create_task(self())


def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"


class NaffQueueManager:
    _queues = {}

    @classmethod
    def get_queue(cls, server_id, voice_state=None):
        if server_id not in cls._queues:
            cls._queues[server_id] = NaffQueue(voice_state)
        return cls._queues[server_id]
