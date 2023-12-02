import requests
from yt_dlp import YoutubeDL

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
headers = {
    "videoId": "video_id",
    "playlistId": "playlistId (if there is a playlist associated with the video (&list=playlist_id) when calling the URL)",
    "context": {
        "client": {
            "hl": "en",
            "gl": "US",
            "clientName": "1 (or WEB)",
            "clientVersion": "desktop_client_version (like 2.20210401.08.00)",
        }
    }
}
data = requests.get('https://www.youtube.com/playlist?list=PLL-LXY9dtjAYQ6cK9SbNCbiYml7O11oMt', headers=headers)
print(data.text)
