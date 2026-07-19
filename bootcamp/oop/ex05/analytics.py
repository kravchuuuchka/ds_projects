import os
from random import randint


class Research:
    def __init__(self, path: str) -> None:
        self.path = path

    def file_reader(self, has_header: bool = True) -> list:
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        with open(self.path) as f:
            lines = f.read().splitlines()

        if has_header:
            if len(lines) < 2:
                raise ValueError("File must have a header and at least one data row")
            header = lines[0].split(",")
            if len(header) != 2:
                raise ValueError("Header must contain exactly two comma-separated columns")
            data_lines = lines[1:]
        else:
            if len(lines) < 1:
                raise ValueError("File is empty")
            data_lines = lines

        result = []
        for line in data_lines:
            parts = line.split(",")
            if len(parts) != 2:
                raise ValueError(f"Invalid row format: '{line}'")
            if parts[0] not in ("0", "1") or parts[1] not in ("0", "1"):
                raise ValueError(f"Row values must be 0 or 1: '{line}'")
            if parts[0] == parts[1]:
                raise ValueError(f"Row must not contain both 0 and 1 equal: '{line}'")
            result.append([int(parts[0]), int(parts[1])])

        return result

    class Calculations:
        def __init__(self, data: list) -> None:
            self.data = data

        def counts(self) -> tuple:
            heads = sum(row[0] for row in self.data)
            tails = sum(row[1] for row in self.data)
            return heads, tails

        def fractions(self, heads: int, tails: int) -> tuple:
            total = heads + tails
            return round(heads / total, 4), round(tails / total, 4)

        def percentages(self, heads: int, tails: int) -> tuple:
            head_frac, tail_frac = self.fractions(heads, tails)
            return round(head_frac * 100, 2), round(tail_frac * 100, 2)

    class Analytics(Calculations):
        def __init__(self, data: list) -> None:
            super().__init__(data)

        def predict_random(self, n: int) -> list:
            result = []
            for _ in range(n):
                head = randint(0, 1)
                result.append([head, 1 - head])
            return result

        def predict_last(self) -> list:
            return self.data[-1]

        def save_file(self, data: str, filename: str, extension: str) -> None:
            with open(f"{filename}.{extension}", "w") as f:
                f.write(data)