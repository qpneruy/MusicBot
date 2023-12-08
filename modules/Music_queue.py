import asyncio
from collections import deque
from typing import Iterator

from interactions import ActiveVoiceState, Embed, ButtonStyle, ActionRow, Button
from interactions.api.voice.audio import BaseAudio


class MusicQueue:
    voice_state: ActiveVoiceState
    _entries: deque
    _item_queued_: asyncio.Event

    def __init__(self, voice_state: ActiveVoiceState):
        self.voice_state = voice_state
        self._entries = deque()
        self.__song_list__ = []
        self._item_queued = asyncio.Event()
        self.task = asyncio.Task

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[BaseAudio]:
        return iter(self._entries)

    async def put(self, audio_d: BaseAudio, avatar_url: str) -> None:
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
        nut = ActionRow(
            Button(
                style=ButtonStyle.LINK,
                label="Link",
                url=f'https://www.youtube.com/watch?v={audio_d.entry["id"]}'
            ),
            Button(
                custom_id="skip_button",
                style=ButtonStyle.GREY,
                label="⏭️ Tiếp theo",
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

    def peek_at_index(self, index: int) -> BaseAudio:
        return self._entries[index]

    async def __playback_queue(self) -> None:
        while self.voice_state.connected:
            if len(self._entries) == 0:
                self.task.cancel()
            if self.voice_state.playing:
                await self.voice_state.wait_for_stopped()
            audio_d = await self.pop()
            _song_msg_ = self.__song_list__.pop()
            _song_msg_[0].set_author('💿 Đang chơi')
            await self.voice_state.channel.send(embed=_song_msg_[0])
            await self.voice_state.channel.send(components=_song_msg_[1], silent=True)
            print('Đang phát nhạc')
            print(audio_d)
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
class MusicQueueManager:
    _queues_ = {}

    @classmethod
    def get_queue(cls, server_id, voice_state: ActiveVoiceState):
        if server_id not in cls._queues_:
            cls._queues_[server_id] = MusicQueue(voice_state)
        return cls._queues_[server_id]
