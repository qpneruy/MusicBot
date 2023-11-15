import os
import requests
import string
import json
import yt_dlp
from yt_dlp import YoutubeDL
from yt_download import AudioYT

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


class VideoInfo:
    def __init__(self):
        self.tokenA = os.getenv('YOUTUBE_API_KEY_1')
        self.tokenB = os.getenv('YOUTUBE_API_KEY_2')
        self.api_key = self.tokenA
        self.search_id = ''
        self.searchvid_url = 'https://www.googleapis.com/youtube/v3/search'
        self.searchppl_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        self.playlist_url = []
        self.paramsVideo = {
            'key': self.api_key,
            'part': 'snippet',
            'type': 'video',
            'maxResults': 1,
            'regionCode': 'VN'
        }
        self.paramsPlaylist = {
            'part': 'snippet,contentDetails,status',
            'maxResults': 200,
            'playlistId': string,
            'key': self.api_key,
        }

    def search_vid(self, search_query: str) -> str | None:
        video_url = None
        self.paramsVideo['q'] = search_query
        response = requests.get(self.searchvid_url, params=self.paramsVideo)
        if response.status_code == 200:
            search_results = response.json()
            if 'items' in search_results and len(search_results['items']) > 0:
                first_video = search_results['items'][0]
                video_id = first_video['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                print("Không tìm thấy video nào.")
        else:
            print(f"Lỗi khi thực hiện tìm kiếm: {response.status_code}")
        return video_url

    async def playlist_get(self, playlist_url: string) -> list | None:
        playlist_id = playlist_url.split('=')[-1]
        self.paramsPlaylist['playlistId'] = playlist_id
        response = requests.get(self.searchppl_url, params=self.paramsPlaylist)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                privacy_status = item['status']['privacyStatus']
                if privacy_status != 'private':
                    self.playlist_url.insert(0, f'https://www.youtube.com/watch?v={video_id}')
            return self.playlist_url
        else:
            print(f"Lỗi khi lấy thông tin về kênh: {response.status_code}")

    def get_uploader_avt(self, url: str | None = None, direct_url: any = None) -> str:
        if direct_url is not None:
            data = direct_url
        else:
            data = youtube_dl.extract_info(url, download=False)
        channel_id = data['channel_id']
        channel_url = f'https://www.googleapis.com/youtube/v3/channels?key={self.api_key}&part=snippet&id={channel_id}'
        channel_response = requests.get(channel_url)
        if channel_response.status_code == 200:
            channel_data = channel_response.json()
            avatar_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
            return avatar_url
        else:
            print(f"Lỗi khi lấy thông tin về kênh: {response.status_code}")
