import json

from util import RefreshInterval, DiskUsage


class Config:
    _path: str
    _interval: RefreshInterval
    _used_threshold: DiskUsage
    _file_directory: str
    _remote_host: str
    _sender_threads: int
    _display_chunk_size: int

    def __init__(self, path: str, interval: RefreshInterval, used_threshold: DiskUsage, file_directory: str,
                 remote_host: str = "127.0.0.1:5000", sender_threads: int = 200, display_chunk_size: int = 100):
        self._path = path
        self._interval = interval
        self._used_threshold = used_threshold
        self._file_directory = file_directory
        self._remote_host = remote_host
        self._sender_threads = sender_threads
        self._display_chunk_size = display_chunk_size

    @classmethod
    def from_file(cls, file: str) -> "Config":
        with open(file, "r") as f:
            data = json.load(f)

        def parse_interval(value):
            if isinstance(value, str):
                try:
                    return RefreshInterval[value]
                except KeyError as exc:
                    raise ValueError(f"Unknown interval name: {value}") from exc
            try:
                return RefreshInterval(value)
            except ValueError as exc:
                raise ValueError(f"Invalid interval value: {value}") from exc

        def parse_used_threshold(value):
            if isinstance(value, str):
                try:
                    return DiskUsage[value]
                except KeyError as exc:
                    raise ValueError(f"Unknown used_threshold name: {value}") from exc
            try:
                return DiskUsage(value)
            except ValueError as exc:
                raise ValueError(f"Invalid used_threshold value: {value}") from exc

        path = data.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("Config missing 'path' string.")

        file_directory = data.get("file_directory", "")
        if file_directory == "":
            raise ValueError("Config missing 'file_directory' string.")

        interval = parse_interval(data.get("interval"))
        used_threshold = parse_used_threshold(data.get("used_threshold"))
        remote_host = data.get("remote_host")
        sender_threads = data.get("sender_threads")
        display_chunk_size = data.get("display_chunk_size")

        config = cls(path, interval, used_threshold, file_directory, remote_host, sender_threads, display_chunk_size)
        return config

    @property
    def path(self) -> str:
        return self._path

    @property
    def interval(self) -> RefreshInterval:
        return self._interval

    @property
    def file_directory(self) -> str:
        return self._file_directory

    @property
    def used_threshold(self) -> DiskUsage:
        return self._used_threshold

    @property
    def host(self) -> str:
        return self._remote_host

    @property
    def sender_threads(self) -> int:
        return self._sender_threads

    @property
    def display_chunk_size(self) -> int:
        return self._display_chunk_size

    def to_dict(self) -> dict:
        return {
            "path": self._path,
            "interval": self._interval.value,
            "used_threshold": self._used_threshold.value,
            "file_directory": self._file_directory,
            "remote_host": self._remote_host,
            "sender_threads": self._sender_threads,
        }
