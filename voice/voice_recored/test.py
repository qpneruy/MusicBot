import requests

url = "https://hocbadientu.vnedu.vn/sllservices/index.php"
params = {
    'callback': 'jQuery1124042229742630956757_1705934314898',
    'call': 'solienlac.getSodiem',
    'mahocsinh': '2107435057',
    'key': 'd33e425220d1f1184a9fb9a477055fd6',
    'namhoc': '2023',
    'tinh_id': '7',
    'dot_diem_id': '0',
    '_': '1705934314902'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://tracuu.vnedu.vn/',
    'Sec-Ch-Ua-Platform': "Windows",
    'cookie': 'BIGipServerAPP_EDU_HBDT=739614474.20480.0000; PHPSESSID=s70ffcn6itrs41vakrcrp7gvt7; sso_key_login=ODdaQXdoNU8xd0k0dEpxRXVFUlVLYnNpZ1dlRUxNMU9tYVNHSlBwM1ZxWEZ4NTdMTHAwQjdhOXk4MlFkOGxRcEZzSjhJYTJXdnNmZkk1WGxhT0k3SDZlZGM5SjdfLjRCVlNNZmVERHlNNHA2MmtFSll5aTN2WTB4by40WnNSRDNjSFQ5cm9yVFYuQW5tTG5ZWmtETGdfdmN1SUtINF8ubDVpajJnb2NiVTEyZVB3NlFhSGR6NjZ0ZGhtTDVVTEY2WEpRM2JwVllyNmQ0RmtYWk1udW13X01BVHJuaDZzakhWU3RPX2IxeXA5MC0%3D',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    print(">>", response.text)
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
