import requests
import tempfile
import pygame
import time

pygame.mixer.init()

_API_URL = 'https://api.yaohud.cn/api/music/wy'
_API_KEY = 'gKdP4sECc4NbbVxz868'
song_name = "撒野"

params = {'key': _API_KEY, 'msg': song_name, 'n': '1'}
resp = requests.post(_API_URL, params=params, timeout=10)
music_url = resp.json()['data']['musicurl']
print("音乐URL：", music_url)

with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
    f.write(requests.get(music_url, timeout=10).content)
    temp_path = f.name

pygame.mixer.music.load(temp_path)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

print("播放完成")
