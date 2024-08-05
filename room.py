from datetime import datetime, timedelta
from PIL import Image

from demistar.olhub import RoomDisplay, timeline


START = datetime(2024, 2, 23, 18, 00)
END = datetime(2024, 2, 25, 17, 00)
ROOMS = {
    "k1a": "Sala 1A",
    "k1b": "Sala 1B",
    "k1c": "Sala 1C",
    "k2": "Sala 2",
    "k3": "Sala 3",
    "k4": "Sala 4",
}


bg = Image.open("bg_ph.jpg")


sch_main = list(timeline.from_file("harmonogram.txt", ["main"], True))
for room in ROOMS.keys():
    sch_room = list(timeline.from_file("harmonogram.txt", [room], False))
    prev: RoomDisplay = None

    now = START
    while now < END:
        if now.hour < 3 or now.hour >= 10:
            print(f"{ROOMS[room]} {now}: ", end="")

            def upcoming(m: timeline.Meeting): return m.end() > now
            display = RoomDisplay(room, ROOMS[room], list(
                filter(upcoming, sch_room)), "Mainroom", list(filter(upcoming, sch_main)), now)

            if RoomDisplay.no_change(prev, display):
                print("no change")
            else:
                display.save_image(bg, True)

            prev = display

        now += timedelta(minutes=30)
