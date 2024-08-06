import math
import os

from datetime import datetime
from PIL import Image, ImageDraw


class ScrollingWriter:
    def __init__(self, prefix: str, bg: Image.Image) -> None:
        self.prefix = prefix
        self.frame = bg.crop((0, 0, 1080, 1920))
        self.draw = ImageDraw.Draw(self.frame)

        # Create subdirectories
        os.makedirs(f"out/{self.prefix}", exist_ok=True)

    def save(self, time: datetime, scrolled: list, window_width: int, progress: bool = False) -> int:
        timestamp = f"{time:%Y%m%dT%H%M}"

        # Nothing to scroll, single frame
        if len(scrolled) == 0:
            if progress:
                print("single frame")
            self.frame.save(f"out/{self.prefix}/{self.prefix}-{timestamp}.jpg")
            return 1

        # Render all frames
        os.makedirs(f"out/{self.prefix}/{self.prefix}-{timestamp}", exist_ok=True)
        length = max(text.width for _, text in scrolled) + window_width
        digits = math.ceil(math.log10(length))

        if progress:
            print(" " * (digits * 2 + 1), end="")

        for i in range(length):
            frame = self.frame.copy()
            frame_draw = ImageDraw.Draw(frame)
            for position, text in scrolled:
                frame_draw.bitmap(position, text.crop(
                    (i - window_width, 0, i, text.height)))

            suffix = str(i).zfill(digits)
            frame.save(
                f"out/{self.prefix}/{self.prefix}-{timestamp}/{self.prefix}-{timestamp}-{suffix}.jpg")

            if progress:
                print("\b" * (digits * 2 + 1) +
                      f"{(i + 1):{digits}}/{length}", end="", flush=True)

        return length
