import math
import os

from datetime import datetime, timedelta
from PIL import Image, ImageFont, ImageDraw

from tritostar import schedule, textdraw


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


TITLE_SIZE = 120
TITLE_STROKE = 6
TITLE_YPOS = TITLE_SIZE * 1.5

LIST_SIZE = 48
LIST_ROW = 80

font_title = ImageFont.truetype("multicolore.otf", TITLE_SIZE)
font_list_big = ImageFont.truetype("gidole.ttf", LIST_SIZE)
font_list_small = ImageFont.truetype("gidole.ttf", int(LIST_SIZE / 2))


bg = Image.open("bg_pt.jpg")


sch = list(schedule.from_file("harmonogram.txt", ROOMS.keys(), True))
prev = list()

now = START
while now < END:
    print(f"{now}: ", end="")

    def upcoming(m: schedule.Meeting): return m.end() > now

    img = bg.crop((0, 0, bg.width, bg.height * 3))
    draw = ImageDraw.Draw(img)

#    textdraw.center(draw, "Mainroom", TITLE_YPOS + TITLE_SIZE * 0.75, img.width,
#                    font=font_title, stroke_width=TITLE_STROKE)

    textdraw.center(draw, "Gry ciche", TITLE_YPOS, img.width,
                    font=font_title, stroke_width=TITLE_STROKE)
    textdraw.center(draw, "i głośne", TITLE_YPOS + TITLE_SIZE *
                    1.1, img.width, font=font_title, stroke_width=TITLE_STROKE)

    scrolled = list()
    title_width = img.width - int(LIST_SIZE * 5.5)
#    title_width = img.width - int(LIST_SIZE * 4)

    y_offset = bg.height
    meetings = list(sorted(filter(upcoming, sch), key=lambda m: m.start))[:16]

    if prev == meetings:
        print("no change")
        now += timedelta(minutes=30)
        continue

    prev = meetings
    for meeting in meetings:
        draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.05),
                  meeting.start.strftime("%H:%M"), "#fff", font=font_list_big)
        draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 1.1),
                  meeting.host, "#fff", font=font_list_small)
        draw.text((img.width - LIST_SIZE * 1.5, y_offset + LIST_SIZE * 0.05),
                  ROOMS[meeting.room].split()[-1], "#fff", font=font_list_big)

        _, _, width, height = draw.textbbox(
            (0, 0), meeting.title, font=font_list_big)
        position = (int(LIST_SIZE * 3.5), int(y_offset + LIST_SIZE * 0.05))
        if width > title_width:
            scrolled.append((position, textdraw.render(
                width, height, meeting.title, font_list_big)))
        else:
            draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 0.05),
                      meeting.title, "#fff", font=font_list_big)

        y_offset += LIST_ROW

    timestamp = f"{now:%Y%m%dT%H%M}"
    now += timedelta(minutes=30)

    # Nothing to scroll, single frame
    if len(scrolled) == 0:
        print("single frame")
        img.save(f"hub/hg-{timestamp}.jpg")
        continue

    # Render all frames
    os.makedirs(f"hub/hg-{timestamp}", exist_ok=True)
    length = max(text.width for _, text in scrolled) + title_width
    digits = math.ceil(math.log10(length))

    print(" " * (digits * 2 + 1), end="")

    for i in range(length):
        frame = img.copy()
        frame_draw = ImageDraw.Draw(frame)
        for position, text in scrolled:
            frame_draw.bitmap(position, text.crop(
                (i - title_width, 0, i, text.height)))
            suffix = str(i).zfill(digits)
            frame.save(
                f"hub/hg-{timestamp}/hg-{timestamp}-{suffix}.jpg")

        print("\b" * (digits * 2 + 1) +
              f"{(i + 1):{digits}}/{length}", end="", flush=True)

    print()
