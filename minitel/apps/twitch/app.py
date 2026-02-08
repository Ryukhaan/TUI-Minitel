import socket
import time

SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICK = "justinfan12345"   # pseudo invité
CHANNEL = "#romainjacques_"

sock = socket.socket()
sock.connect((SERVER, PORT))

sock.send(f"NICK {NICK}\r\n".encode())
sock.send(f"JOIN {CHANNEL}\r\n".encode())

while True:
    resp = sock.recv(2048).decode("utf-8", errors="ignore")

    for line in resp.split("\r\n"):
        if line.startswith("PING"):
            sock.send("PONG :tmi.twitch.tv\r\n".encode())

        elif "PRIVMSG" in line:
            prefix, message = line.split("PRIVMSG", 1)
            user = prefix.split("!")[0][1:]
            text = message.split(":", 1)[1]
            print(f"{line}")
    time.sleep(0.01)