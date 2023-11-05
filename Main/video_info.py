import os
import requests
import string


class VideoInfo:
    def __init__(self):
        self.tokenA = os.getenv('YOUTUBE_API_KEY_1')
        self.tokenB = os.getenv('YOUTUBE_API_KEY_2')
        self.api_key = self.tokenB
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
        response = requests.get(self.search_url, params=self.paramsVideo)
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
            self.api_key = self.tokenB
            self.paramsVideo['q'] = '6POZlJAZsok'
            test = requests.get(self.searchvid_url, params=self.paramsVideo)
            
            if test.status_code != 200:
                print('PLAYLIST | Đã vượt định mức API A & B')
                print(f"Lỗi khi lấy thông tin về video: {response.status_code}")
                return None
        return self.playlist_get(playlist_url)

    def get_uploader_avt(self, url: str) -> str | None:
        search_query = url.split('=')[-1]
        self.paramsVideo['q'] = search_query
        response = requests.get(self.searchvid_url, params=self.paramsVideo)
        if response.status_code == 200:
            video_data = response.json()
            channel_id = video_data['items'][0]['snippet']['channelId']
            channel_url = f'https://www.googleapis.com/youtube/v3/channels?key={self.api_key}&part=snippet&id={channel_id}'
            channel_response = requests.get(channel_url)
            if channel_response.status_code == 200:
                channel_data = channel_response.json()
                avatar_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
                return avatar_url
            else:
                print(f"Lỗi khi lấy thông tin về kênh: {response.status_code}")
        else:
            self.api_key = self.tokenB
            self.paramsVideo['q'] = '6POZlJAZsok'
            test = requests.get(self.searchvid_url, params=self.paramsVideo)
            if test.status_code != 200:
                print('UPLOAD | Đã vượt định mức API A & B')
                print(f"Lỗi khi lấy thông tin về video: {response.status_code}")
                return None
        return self.get_uploader_avt(url)

    def peek(self, positions: int = 1) -> bool | None:
        try:
            refence = self.playlist_url[positions - 1]
            if refence is not None:
                return True
            else:
                return False
        except IndexError:
            return None
