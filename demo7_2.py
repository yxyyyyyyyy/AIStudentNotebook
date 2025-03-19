import yt_dlp

url = "https://youtube.com/watch?v=dA1cHGACXCo"
ydl_opts = {}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(url, download=False)
    print("标题:", info_dict["title"])
