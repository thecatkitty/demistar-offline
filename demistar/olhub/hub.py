from datetime import datetime
from PIL import Image

from . import textdraw
from .config import Configuration
from .metrics.hub import *
from .timeline import Meeting
from .writer import ScrollingWriter


class HubDisplay:
    def __init__(self, prefix: str, caption: list[str], upcoming: list[Meeting], config: Configuration, now: datetime) -> None:
        self.time = now
        self.prefix = prefix
        self.caption = caption
        self.rooms = config.rooms
        self.upcoming = upcoming[:16]
        self.fonts = config.hub_fonts

    def print(self) -> None:
        print(f"HubDisplay at {self.time}:")
        for meeting in self.upcoming:
            print("   ", meeting)
        print()

    def save_image(self, top_img: Image.Image, progress: bool = False) -> int:
        writer = ScrollingWriter(self.prefix, top_img)
        img = writer.frame
        draw = writer.draw

        if 1 == len(self.caption):
            textdraw.center(draw, self.caption[0], TITLE_YPOS + TITLE_SIZE *
                            0.75, img.width, font=self.fonts['spot'], stroke_width=TITLE_STROKE)
        elif 2 == len(self.caption):
            textdraw.center(
                draw, self.caption[0], TITLE_YPOS, img.width, font=self.fonts['spot'], stroke_width=TITLE_STROKE)
            textdraw.center(draw, self.caption[1], TITLE_YPOS + TITLE_SIZE *
                            1.1, img.width, font=self.fonts['spot'], stroke_width=TITLE_STROKE)
        else:
            raise ValueError("Too many hub caption lines")

        scrolled = list()
        title_width = img.width - int(LIST_SIZE * 5.5)

        y_offset = top_img.height
        for meeting in self.upcoming:
            draw.text((LIST_SIZE * 0.5, y_offset + LIST_SIZE * 0.05),
                      meeting.start.strftime("%H:%M"), textdraw.FILL, font=self.fonts['listl'])
            draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 1.1),
                      meeting.host, textdraw.FILL, font=self.fonts['lists'])
            draw.text((img.width - LIST_SIZE * 1.5, y_offset + LIST_SIZE * 0.05),
                      self.rooms[meeting.room][1], textdraw.FILL, font=self.fonts['listl'])

            _, _, width, height = draw.textbbox(
                (0, 0), meeting.title, font=self.fonts['listl'])
            position = (int(LIST_SIZE * 3.5), int(y_offset + LIST_SIZE * 0.05))
            if width > title_width:
                scrolled.append((position, textdraw.render(
                    width, height, meeting.title, self.fonts['listl'])))
            else:
                draw.text((LIST_SIZE * 3.5, y_offset + LIST_SIZE * 0.05),
                          meeting.title, textdraw.FILL, font=self.fonts['listl'])

            y_offset += LIST_ROW

        result = writer.save(self.time, scrolled, title_width, progress)
        if progress:
            print()
        return result

    def no_change(self, prev: object) -> bool:
        if prev is None:
            return False

        return all(l.title == r.title for l, r in zip(prev.upcoming, self.upcoming))
