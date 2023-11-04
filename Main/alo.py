import requests
import os
import json
# Thay thế bằng API key của bạn
token = os.getenv('YOUTUBE_API_KEY')
api_key = token  # Thay YOUR_API_KEY bằng khóa API của bạn
API_KEY = api_key
video_id = 'JzFW_-U_Zo8'
video_url = f'https://www.googleapis.com/youtube/v3/videos?key={API_KEY}&part=snippet&id={video_id}'
video_response = requests.get(video_url)

if video_response.status_code == 200:
    video_data = video_response.json()
    channel_id = video_data['items'][0]['snippet']['channelId']

    # Bước 2: Lấy thông tin về kênh
    channel_url = f'https://www.googleapis.com/youtube/v3/channels?key={API_KEY}&part=snippet&id={channel_id}'
    channel_response = requests.get(channel_url)

    if channel_response.status_code == 200:
        channel_data = channel_response.json()
        avatar_url = channel_data['items'][0]['snippet']['thumbnails']['default']['url']
        print(f"Link ảnh đại diện của kênh: {avatar_url}")
    else:
        print(f"Lỗi khi lấy thông tin về kênh: {channel_response.status_code}")
else:
    print(f"Lỗi khi lấy thông tin về video: {video_response.status_code}")
