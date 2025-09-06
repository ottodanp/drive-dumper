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

    def print_stats(self, files: int, directories: int, size: int, time: float) -> None:
        print(f"Found {files} files and {directories} directories ({self.format_bytes(size)}) in {time:.2f} seconds.")

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
    def disk_full_notification():
        print("Disk is full, moving files")

    @staticmethod
    def calculate_size(size: int, divisor: SizeDivisor) -> float:
        return round((size / divisor.value), 3)
