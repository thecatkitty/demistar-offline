import math
import os
import textwrap

from datetime import datetime
from PIL import Image, ImageDraw

from . import textdraw
from .config import Configuration
from .metrics.room import *
from .timeline import Meeting


class RoomDisplay:
    def __init__(self, room: str, room_caption: str, upcoming: list[Meeting], featured_caption: str, featured: list[Meeting], config: Configuration, now: datetime) -> None:
        self.time = now
        self.featured_caption = featured_caption
        self.featured = featured[:2]
        self.room_caption = room_caption
        self.room = room
        self.fonts = config.room_fonts

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
                            font=self.fonts['spots'], stroke_width=HOST_STROKE)

            # Spotlight appointment title
            title = textwrap.wrap(self.spotlight.title, TITLE_WRAP)
            y_offset = TITLE_YPOS
            for line in title:
                textdraw.center(draw, line, y_offset, img.width,
                                font=self.fonts['spotl'], stroke_width=TITLE_STROKE)
                y_offset += TITLE_SIZE * 1.1

            # Spotlight appointment host
            y_offset += HOST_SIZE
            host = textwrap.wrap(self.spotlight.host, HOST_WRAP)
            for line in host:
                textdraw.center(draw, line, y_offset, img.width,
                                font=self.fonts['spots'], stroke_width=HOST_STROKE)
                y_offset += HOST_SIZE

        # Room
        draw.text((HOST_SIZE / 2, top_half.height - 2 * HOST_SIZE),
                  self.room_caption, textdraw.FILL, font=self.fonts['spotl'], stroke_width=TITLE_STROKE, stroke_fill=textdraw.STROKE)

        scrolled = list()
        title_width = img.width - LIST_SIZE * 4

        # Upcoming appointments
        y_offset = top_half.height
        for meeting in self.upcoming:
            draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.5),
                      meeting.start.strftime("%H:%M"), textdraw.FILL, font=self.fonts['listl'])
            draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 1.75),
                      meeting.host, textdraw.FILL, font=self.fonts['lists'])

            _, _, width, height = draw.textbbox(
                (0, 0), meeting.title, font=self.fonts['listl'])
            position = (int(LIST_SIZE * 3.5), int(y_offset + LIST_SIZE / 2))
            if width > title_width:
                scrolled.append((position, textdraw.render(
                    width, height, meeting.title, self.fonts['listl'])))
            else:
                draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE / 2),
                          meeting.title, textdraw.FILL, font=self.fonts['listl'])

            y_offset += LIST_ROW

        # Featured header
        y_offset = img.height - LIST_ROW * 3.5
        draw.text((LIST_SIZE / 2, y_offset + TITLE_SIZE),
                  self.featured_caption, textdraw.FILL, font=self.fonts['spotl'])
        y_offset += LIST_ROW * 1.5

        # Featured appointments
        for meeting in self.featured:
            draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.5),
                      meeting.start.strftime("%H:%M"), textdraw.FILL, font=self.fonts['listl'])

            _, _, width, height = draw.textbbox(
                (0, 0), meeting.title, font=self.fonts['listl'])
            position = (int(LIST_SIZE * 3.5), int(y_offset + LIST_SIZE / 2))
            if width > title_width:
                scrolled.append((position, textdraw.render(
                    width, height, meeting.title, self.fonts['listl'])))
            else:
                draw.text(position, meeting.title, textdraw.FILL,
                          font=self.fonts['listl'])

            y_offset += LIST_ROW

        # Create subdirectories
        os.makedirs(f"out/{self.room}", exist_ok=True)
        timestamp = f"{self.time:%Y%m%dT%H%M}"

        # Nothing to scroll, single frame
        if len(scrolled) == 0:
            if progress:
                print("single frame")
            img.save(f"out/{self.room}/{self.room}-{timestamp}.jpg")
            return

        # Render all frames
        os.makedirs(f"out/{self.room}/{self.room}-{timestamp}", exist_ok=True)
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
                    f"out/{self.room}/{self.room}-{timestamp}/{self.room}-{timestamp}-{suffix}.jpg")

            if progress:
                print("\b" * (digits * 2 + 1) +
                      f"{(i + 1):{digits}}/{length}", end="", flush=True)

        if progress:
            print()

    def no_change(self, prev: object):
        if prev is None:
            return False

        left_spotlight = "" if prev.spotlight is None else prev.spotlight.title
        right_spotlight = "" if self.spotlight is None else self.spotlight.title
        left_featured = "" if len(
            prev.featured) == 0 else prev.featured[0].title
        right_featured = "" if len(
            self.featured) == 0 else self.featured[0].title
        return left_spotlight == right_spotlight and left_featured == right_featured
