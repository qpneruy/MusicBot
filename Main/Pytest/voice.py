import requests

url = 'https://api.fpt.ai/hmi/tts/v5'

payload = 'xin chào'
headers = {
    'api-key': '12y0uP7g2NK8JlweFlyd49Pk4j2a4eIK',
    'speed': '',
    'voice': 'banmai'
}

response = requests.request('POST', url, data=payload.encode('utf-8'), headers=headers)

print(response.text)