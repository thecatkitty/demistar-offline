from datetime import datetime, timedelta
from PIL import Image

from demistar.olhub import HubDisplay, timeline


START = datetime(2024, 2, 23, 18, 00)
END = datetime(2024, 2, 25, 17, 00)
ROOMS = {
#    "main": "Mainroom",
#    "k1a": "Sala 1A",
#    "k1b": "Sala 1B",
#    "k1c": "Sala 1C",
#    "k2": "Sala 2",
#    "k3": "Sala 3",
#    "k4": "Sala 4",
    "gc": "Gry C",
    "gg": "Gry G",
}


bg = Image.open("bg_pt.jpg")


sch = list(timeline.from_file("harmonogram.txt", ROOMS.keys(), True))
prev: HubDisplay = None

now = START
while now < END:
    print(f"{now}: ", end="")

    def upcoming(m: timeline.Meeting): return m.end() > now
    display = HubDisplay(["Gry ciche", "i głośne"], list(
        sorted(filter(upcoming, sch), key=lambda m: m.start)), ROOMS, now)

    if HubDisplay.no_change(prev, display):
        print("no change")
    else:
        display.save_image(bg, True)

    prev = display
    now += timedelta(minutes=30)
