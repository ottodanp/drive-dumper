from config import Config
from util import SizeDivisor

DIVISOR_EXTENSIONS = {
    SizeDivisor.GB: "GB",
    SizeDivisor.MB: "MB",
    SizeDivisor.KB: "KB",
    SizeDivisor.BYTES: "BYTES",
}


class Display:
    _config: Config

    def __init__(self):
        return

    def print_stats(self, files: int, directories: int, size: int) -> None:
        print(f"{files} files, {directories} directories, {self.format_bytes(size)}")

    def format_bytes(self, size: int) -> str:
        if size > SizeDivisor.GB.value:
            div = SizeDivisor.GB
        elif size > SizeDivisor.MB.value:
            div = SizeDivisor.MB
        elif size > SizeDivisor.KB.value:
            div = SizeDivisor.KB
        else:
            div = SizeDivisor.BYTES

        return f"{self.calculate_size(size, div)}{DIVISOR_EXTENSIONS[div]}"

    @staticmethod
    def calculate_size(size: int, divisor: SizeDivisor) -> float:
        return round((size / divisor.value), 3)
