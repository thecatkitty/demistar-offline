from datetime import timedelta
from PIL import Image

from demistar.olhub import Configuration, RoomDisplay, timeline

bg = Image.open("bg_ph.jpg")


config = Configuration("demistar.ini")
sch_main = list(timeline.from_file(config.schedule_file, ["main"], True))
for room in config.rooms.keys():
    sch_room = list(timeline.from_file(config.schedule_file, [room], False))
    prev: RoomDisplay = None

    now = config.start_time
    while now < config.end_time:
        if now.hour < 3 or now.hour >= 10:
            print(f"{config.rooms[room]} {now}: ", end="")

            def upcoming(m: timeline.Meeting): return m.end() > now
            display = RoomDisplay(room, config.rooms[room], list(
                filter(upcoming, sch_room)), "Mainroom", list(filter(upcoming, sch_main)), config, now)

            if RoomDisplay.no_change(prev, display):
                print("no change")
            else:
                display.save_image(bg, True)

            prev = display

        now += timedelta(minutes=30)
