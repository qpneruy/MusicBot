import asyncio
import random
from collections import deque
from typing import Iterator
from interactions import ActiveVoiceState
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

    def put(self, audio_d: BaseAudio) -> None:
        self._entries.append(audio_d)
        self._item_queued.set()

    def get_list(self) -> list:
        return self.__song_list__

    def put_first(self, audio_d: BaseAudio) -> None:
        self._entries.appendleft(audio_d)
        self._item_queued.set()

    async def pop(self) -> BaseAudio:
        if len(self) == 0:
            await self._item_queued.wait()
        item = self._entries.popleft()
        # self._item_queued.clear()
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
        # while self.voice_state.connected:
        #     if self.voice_state.playing:
        #         await self.voice_state.wait_for_stopped()
        #     audio = await self.pop()
        #     print(f'audio be nggoai {audio}')
        #     current_audio = audio  # Lưu trữ audio hiện tại
        #     embed = self.__song_list__.pop()
        #     await self.voice_state.channel.send(embed=embed)
        #     print(f' da de quy {audio}')
        #     await self.voice_state.play(audio)
        #     if self.loopstate:
        #             print("đmdmdmđmmd")
        #             print(current_audio)
        #             self.put_first(current_audio)  # Thêm lại audio hiện tại vào hàng đợi nếu loopstate là True
        #             #audio = await self.pop()
        #             #await self.voice_state.play(current_audio)
        #             await self.__playback_queue()

        # >> code lặp cần fix << >>> put_at_index tránh việc đang lặp mà thêm bài hát vào
        while self.voice_state.connected:
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            if self.peek() is not None:
                audio_d = await self.pop()
                if audio_d is not None:
                    self.last = audio_d
                    embed = self.__song_list__.pop()
                    await self.voice_state.channel.send(embed=embed)
                await self.voice_state.play(audio_d)

    async def _stop(self) -> None:
        await self.voice_state.stop()

    async def __call__(self) -> None:
        await self.__playback_queue()

    def start(self) -> None:
        if self._current_task is not None:
            self._current_task.cancel()
            self._stop()
        self._current_task = asyncio.create_task(self())
