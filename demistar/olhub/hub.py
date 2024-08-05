import math
import os

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from . import textdraw
from .timeline import Meeting

TITLE_SIZE = 120
TITLE_STROKE = 6
TITLE_YPOS = TITLE_SIZE * 1.5

LIST_SIZE = 48
LIST_ROW = 80

font_title = ImageFont.truetype("multicolore.otf", TITLE_SIZE)
font_list_big = ImageFont.truetype("gidole.ttf", LIST_SIZE)
font_list_small = ImageFont.truetype("gidole.ttf", int(LIST_SIZE / 2))


class HubDisplay:
    def __init__(self, caption: list[str], upcoming: list[Meeting], rooms: dict[str, str], now: datetime) -> None:
        self.time = now
        self.caption = caption
        self.rooms = rooms
        self.upcoming = upcoming[:16]

    def print(self) -> None:
        print(f"HubDisplay at {self.time}:")
        for meeting in self.upcoming:
            print("   ", meeting)
        print()

    def save_image(self, top_img: Image.Image, progress: bool = False) -> int:
        img = top_img.crop((0, 0, top_img.width, top_img.height * 3))
        draw = ImageDraw.Draw(img)

        if 1 == len(self.caption):
            textdraw.center(draw, self.caption[0], TITLE_YPOS + TITLE_SIZE *
                            0.75, img.width, font=font_title, stroke_width=TITLE_STROKE)
        elif 2 == len(self.caption):
            textdraw.center(
                draw, self.caption[0], TITLE_YPOS, img.width, font=font_title, stroke_width=TITLE_STROKE)
            textdraw.center(draw, self.caption[1], TITLE_YPOS + TITLE_SIZE *
                            1.1, img.width, font=font_title, stroke_width=TITLE_STROKE)
        else:
            raise ValueError("Too many hub caption lines")

        scrolled = list()
        title_width = img.width - (int(LIST_SIZE * 5.5) if 2 == len(self.caption) else int(LIST_SIZE * 4))

        y_offset = top_img.height
        for meeting in self.upcoming:
            draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.05),
                      meeting.start.strftime("%H:%M"), "#fff", font=font_list_big)
            draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 1.1),
                      meeting.host, "#fff", font=font_list_small)
            draw.text((img.width - LIST_SIZE * 1.5, y_offset + LIST_SIZE * 0.05),
                      self.rooms[meeting.room].split()[-1], "#fff", font=font_list_big)

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

        timestamp = f"{self.time:%Y%m%dT%H%M}"

        # Nothing to scroll, single frame
        if len(scrolled) == 0:
            if progress:
                print("single frame")
            img.save(f"hub/hg-{timestamp}.jpg")
            return 1

        # Render all frames
        os.makedirs(f"hub/hg-{timestamp}", exist_ok=True)
        length = max(text.width for _, text in scrolled) + title_width
        digits = math.ceil(math.log10(length))

        if progress:
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

            if progress:
                print("\b" * (digits * 2 + 1) +
                      f"{(i + 1):{digits}}/{length}", end="", flush=True)

        if progress:
            print()

        return length

    @staticmethod
    def no_change(left: object, right: object):
        if left is None:
            return False

        return all(l.title == r.title for l, r in zip(left.upcoming, right.upcoming))