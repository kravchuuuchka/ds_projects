import sys
import os


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
        def counts(self, data: list) -> tuple:
            heads = sum(row[0] for row in data)
            tails = sum(row[1] for row in data)
            return heads, tails

        def fractions(self, heads: int, tails: int) -> tuple:
            total = heads + tails
            return round(heads / total, 4), round(tails / total, 4)


def main() -> None:
    try:
        if len(sys.argv) not in (2, 3):
            raise ValueError("Usage: python3 first_nest.py <path_to_csv> [true|false]")
        research = Research(sys.argv[1])
        if len(sys.argv) == 3:
            if sys.argv[2].lower() not in ("true", "false"):
                raise ValueError("Second argument must be 'true' or 'false'")
            data = research.file_reader(has_header=sys.argv[2].lower() == "true")
        else:
            data = research.file_reader()
        print(data)
        calc = Research.Calculations()
        heads, tails = calc.counts(data)
        print(heads, tails)
        head_frac, tail_frac = calc.fractions(heads, tails)
        print(head_frac, tail_frac)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()