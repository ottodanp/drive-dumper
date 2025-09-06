import json

from structures import RefreshInterval, DiskUsage


class Config:
    _path: str
    _interval: RefreshInterval
    _used_threshold: DiskUsage
    _file_directory: str

    def __init__(self, path: str, interval: RefreshInterval, used_threshold: DiskUsage, file_directory: str):
        self._path = path
        self._interval = interval
        self._used_threshold = used_threshold
        self._file_directory = file_directory

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

        config = cls(path, interval, used_threshold, file_directory)
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

    def to_dict(self) -> dict:
        return {
            "path": self._path,
            "interval": self._interval.value,
            "used_threshold": self._used_threshold.value,
            "file_directory": self._file_directory
        }
