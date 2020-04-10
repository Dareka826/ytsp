#!/usr/bin/python
import subprocess, requests

api_url = "https://www.googleapis.com/youtube/v3/"
api_key = "AIzaSyAivZu0sEhrheCHLDy33ws6BWjKDBmjxPA"
max_results = 10
region_code = "US"

playerv = "mpv"
playera = "mpv --no-video --player-operation-mode=pseudo-gui"

colors = {
    "num": "\u001b[0m",
    "id": "\u001b[35m",
    "title": "\u001b[0m",
    "channel": "\u001b[33m",
    "time": "\u001b[32m",
    "duration": "\u001b[35m",
    "reset": "\u001b[0m"
}

query = ""
next_page_token = ""
num = 0
videos = []

help_txt = """ytsp commands:
    h - display this
    c - clear terminal
    s - search
    n - next page
    v[n] - play entry [n] (video)
    a[n] - play entry [n] (audio)
    i[n] - show info about entry [n]"""

def get_duration(vid):
    response = requests.get(
        api_url + "videos",
        params = (
            ("part", "contentDetails"),
            ("key", api_key),
            ("id", vid),
            ("fields", "items/contentDetails/duration")
        ))
    return response.json()["items"][0]["contentDetails"]["duration"].replace("PT", "").replace("H", ":").replace("M", ":").replace("S", "")

def search(query, pageToken=""):
    response = requests.get(
        api_url + "search",
        params=(
            ("part", "snippet"),
            ("key", api_key),
            ("type", "video"),
            ("regionCode", region_code),
            ("fields", "items(snippet(title,channelTitle,description,publishedAt),id/videoId),nextPageToken"),
            ("pageToken", pageToken),
            ("maxResults", str(max_results)),
            ("q", query)
        ))

    if response.status_code != 200:
        print("ERROR: Failed to communicate with youtube api")
        return

    j = response.json()

    global num, next_page_token, videos
    next_page_token = j["nextPageToken"]

    for item in j["items"]:
        videos.append({
            "n": str(num),
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "time": item["snippet"]["publishedAt"],
            "description": item["snippet"]["description"],
            "duration": get_duration(item["id"]["videoId"])
        })
        num += 1

def print_videos():
    for v in videos:
        print(
            colors["num"] + v["n"] + ": " +
            colors["id"] + v["id"] + " " +
            colors["title"] + v["title"] + " " +
            colors["duration"] + "(" + v["duration"] + ") " +
            colors["channel"] + v["channel"] + " " +
            colors["reset"]
        )

# ===== MAIN LOOP =====
while True:
    try:
        cmd = input("> ")
    except:
        print()
        exit(1)

    if len(cmd) == 0:
        print("?")

    # Display help
    elif cmd[0] == "h" or cmd[0] == "?":
        print(help_txt)

    # Search
    elif cmd[0] == "s":
        if len(cmd) > 1:
            if cmd[1] == " ":
                query = cmd[1:]
            else:
                query = cmd[2:]
        else:
            query = input("q: ")
        num = 0
        videos = []
        search(query)
        print_videos()

    # Query next page
    elif cmd[0] == "n":
        if next_page_token != "":
            search(query, next_page_token)
            print_videos()
        else:
            print("Search first")

    # Play video
    elif cmd[0] == "v":
        if len(cmd) == 1:
            n = input("n: ")
        else:
            n = cmd[1:]

        for v in videos:
            if v["n"] == n:
                subprocess.call(playerv + " https://www.youtube.com/watch?v=" + v["id"] + " >/dev/null 2>&1 &", shell=True)
                break

    # Play audio
    elif cmd[0] == "a":
        if len(cmd) == 1:
            n = input("n: ")
        else:
            n = cmd[1:]

        for v in videos:
            if v["n"] == n:
                subprocess.call(playera + " https://www.youtube.com/watch?v=" + v["id"] + " >/dev/null 2>&1 &", shell=True)
                break

    # Display information
    elif cmd[0] == "i":
        if len(cmd) == 1:
            n = input("n: ")
        else:
            n = cmd[1:]

        for v in videos:
            if v["n"] == n:
                print(colors["time"] + v["time"] + "\n" + colors["reset"] + v["description"])

    # Clear screen
    elif cmd[0] == "c":
        subprocess.run("clear")

    else:
        print("?")

