import math
import os
import textwrap

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from . import textdraw
from .schedule import Meeting


TITLE_SIZE = 80
TITLE_STROKE = 4
TITLE_YPOS = TITLE_SIZE * 2
TITLE_WRAP = 18

HOST_SIZE = int(TITLE_SIZE * 2 / 3)
HOST_STROKE = int(TITLE_STROKE * 0.75)
HOST_WRAP = int(18 * 3 / 2)

LIST_SIZE = HOST_SIZE
LIST_ROW = 128

font_spotlight_big = ImageFont.truetype("multicolore.otf", TITLE_SIZE)
font_spotlight_small = ImageFont.truetype("multicolore.otf", HOST_SIZE)
font_list_big = ImageFont.truetype("gidole.ttf", LIST_SIZE)
font_list_small = ImageFont.truetype("gidole.ttf", int(LIST_SIZE / 2))


class RoomDisplay:
    def __init__(self, room: str, room_caption: str, upcoming: list[Meeting], featured_caption: str, featured: list[Meeting], now: datetime) -> None:
        self.time = now
        self.featured_caption = featured_caption
        self.featured = featured[:2]
        self.room_caption = room_caption
        self.room = room

        if len(upcoming) == 0:
            self.spotlight = None
            self.upcoming = list()
        elif upcoming[0].start <= now:
            self.spotlight = upcoming[0]
            self.upcoming = upcoming[1:5]
        else:
            self.spotlight = None
            self.upcoming = upcoming[:4]

    def print(self):
        print(f"RoomDisplay at {self.time}:")
        if self.spotlight is not None:
            print("  >", self.spotlight)
        for meeting in self.upcoming:
            print("   ", meeting)
        print("Featured:")
        for meeting in self.featured:
            print("   ", meeting)
        print()

    def save_image(self, top_half: Image.Image, progress: bool = False):
        img = top_half.crop((0, 0, top_half.width, top_half.height * 2))
        draw = ImageDraw.Draw(img)

        if self.spotlight is not None:
            # Spotlight appointment begin and end time
            timespan = f"{self.spotlight.start:%H:%M} - {self.spotlight.end():%H:%M}"
            textdraw.center(draw, timespan, HOST_SIZE, img.width,
                            font=font_spotlight_small, stroke_width=HOST_STROKE)

            # Spotlight appointment title
            title = textwrap.wrap(self.spotlight.title, TITLE_WRAP)
            y_offset = TITLE_YPOS
            for line in title:
                textdraw.center(draw, line, y_offset, img.width,
                                font=font_spotlight_big, stroke_width=TITLE_STROKE)
                y_offset += TITLE_SIZE * 1.1

            # Spotlight appointment host
            y_offset += HOST_SIZE
            host = textwrap.wrap(self.spotlight.host, HOST_WRAP)
            for line in host:
                textdraw.center(draw, line, y_offset, img.width,
                                font=font_spotlight_small, stroke_width=HOST_STROKE)
                y_offset += HOST_SIZE

        # Room
        draw.text((HOST_SIZE / 2, top_half.height - 2 * HOST_SIZE),
                  self.room_caption, "#fff", font=font_spotlight_big, stroke_width=TITLE_STROKE, stroke_fill="#000")

        scrolled = list()
        title_width = img.width - LIST_SIZE * 4

        # Upcoming appointments
        y_offset = top_half.height
        for meeting in self.upcoming:
            draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.5),
                      meeting.start.strftime("%H:%M"), "#fff", font=font_list_big)
            draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 1.75),
                      meeting.host, "#fff", font=font_list_small)

            _, _, width, height = draw.textbbox(
                (0, 0), meeting.title, font=font_list_big)
            position = (int(LIST_SIZE * 3.5), int(y_offset + LIST_SIZE / 2))
            if width > title_width:
                scrolled.append((position, textdraw.render(
                    width, height, meeting.title, font_list_big)))
            else:
                draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE / 2),
                          meeting.title, "#fff", font=font_list_big)

            y_offset += LIST_ROW

        # Featured header
        y_offset = img.height - LIST_ROW * 3.5
        draw.text((LIST_SIZE / 2, y_offset + TITLE_SIZE),
                  self.featured_caption, "#fff", font=font_spotlight_big)
        y_offset += LIST_ROW * 1.5

        # Featured appointments
        for meeting in self.featured:
            draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.5),
                      meeting.start.strftime("%H:%M"), "#fff", font=font_list_big)

            _, _, width, height = draw.textbbox(
                (0, 0), meeting.title, font=font_list_big)
            position = (int(LIST_SIZE * 3.5), int(y_offset + LIST_SIZE / 2))
            if width > title_width:
                scrolled.append((position, textdraw.render(
                    width, height, meeting.title, font_list_big)))
            else:
                draw.text(position, meeting.title, "#fff", font=font_list_big)

            y_offset += LIST_ROW

        # Create subdirectories
        os.makedirs(f"room/{self.room}", exist_ok=True)
        timestamp = f"{self.time:%Y%m%dT%H%M}"

        # Nothing to scroll, single frame
        if len(scrolled) == 0:
            if progress:
                print("single frame")
            img.save(f"room/{self.room}-{timestamp}.jpg")
            return

        # Render all frames
        os.makedirs(f"room/{self.room}/{self.room}-{timestamp}", exist_ok=True)
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
                    f"room/{self.room}/{self.room}-{timestamp}/{self.room}-{timestamp}-{suffix}.jpg")

            if progress:
                print("\b" * (digits * 2 + 1) + f"{(i + 1):{digits}}/{length}", end="", flush=True)

        if progress:
            print()


    @staticmethod
    def no_change(left: object, right: object):
        if left is None:
            return False

        left_spotlight = "" if left.spotlight is None else left.spotlight.title
        right_spotlight = "" if right.spotlight is None else right.spotlight.title
        left_featured = "" if len(left.featured) == 0 else left.featured[0].title
        right_featured = "" if len(
            right.featured) == 0 else right.featured[0].title
        return left_spotlight == right_spotlight and left_featured == right_featured
