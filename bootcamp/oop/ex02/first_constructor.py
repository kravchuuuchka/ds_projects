import sys
import os


class Research:
    def __init__(self, path: str) -> None:
        self.path = path

    def file_reader(self) -> str:
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        with open(self.path) as f:
            lines = f.read().splitlines()

        if len(lines) < 2:
            raise ValueError("File must have a header and at least one data row")

        header = lines[0].split(",")
        if len(header) != 2:
            raise ValueError("Header must contain exactly two comma-separated columns")

        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) != 2:
                raise ValueError(f"Invalid row format: '{line}'")
            if parts[0] not in ("0", "1") or parts[1] not in ("0", "1"):
                raise ValueError(f"Row values must be 0 or 1: '{line}'")
            if parts[0] == parts[1]:
                raise ValueError(f"Row must not contain both 0 and 1 equal: '{line}'")

        return "\n".join(lines)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python3 first_constructor.py <path_to_csv>")
        print(Research(sys.argv[1]).file_reader())
    except Exception as e:
        print(e)