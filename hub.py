from datetime import timedelta
from PIL import Image

from demistar.olhub import Configuration, HubDisplay, timeline


bg = Image.open("bg_pt.jpg")

config = Configuration("demistar.ini")
sch = list(timeline.from_file(config.schedule_file, config.rooms.keys(), True))
prev: HubDisplay = None

now = config.start_time
while now < config.end_time:
    print(f"{now}: ", end="")

    def upcoming(m: timeline.Meeting): return m.end() > now
    display = HubDisplay(["Gry ciche", "i głośne"], list(
        sorted(filter(upcoming, sch), key=lambda m: m.start)), config, now)

    if HubDisplay.no_change(prev, display):
        print("no change")
    else:
        display.save_image(bg, True)

    prev = display
    now += timedelta(minutes=30)
