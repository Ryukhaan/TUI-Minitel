import streamlink
import subprocess

streams = streamlink.streams("https://www.twitch.tv/romainjacques_")
CHUNK_SIZE = 1024 * 1024  # 1 Mo, à ajuster selon RAM et débit


best = streams["160p"]
fd = best.open()

ffmpeg = subprocess.Popen(
    ["ffmpeg", "-i", "pipe:0", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

# lire quelques chunks pour avoir une frame complète
data = fd.read(CHUNK_SIZE)
ffmpeg.stdin.write(data)
ffmpeg.stdin.flush()

img_bytes = ffmpeg.stdout.read()
with open("frame.png", "wb") as f:
    f.write(img_bytes)