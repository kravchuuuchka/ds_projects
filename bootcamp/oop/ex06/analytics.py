import os
import logging
import requests
from random import randint
from config import tg_channel, tg_url, log_file

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)


class Research:
    def __init__(self, path: str) -> None:
        logging.debug(f"Initializing Research with path: {path}")
        self.path = path

    def file_reader(self, has_header: bool = True) -> list:
        logging.debug("Reading the file and validating its contents")

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

    def send_telegram(self, message: str) -> None:
        logging.debug("Sending a message to Telegram")
        try:
            payload = {"chat_id": tg_channel, "text": message}
            requests.post(tg_url, json=payload, timeout=5)
        except Exception:
            logging.debug("Failed to send Telegram message")

    class Calculations:
        def __init__(self, data: list) -> None:
            logging.debug(f"Initializing Calculations with {len(data)} rows")
            self.data = data

        def counts(self) -> tuple:
            logging.debug("Calculating the counts of heads and tails")
            heads = sum(row[0] for row in self.data)
            tails = sum(row[1] for row in self.data)
            return heads, tails

        def fractions(self, heads: int, tails: int) -> tuple:
            logging.debug("Calculating the fractions of heads and tails")
            total = heads + tails
            return round(heads / total, 4), round(tails / total, 4)

        def percentages(self, heads: int, tails: int) -> tuple:
            logging.debug("Calculating the percentages of heads and tails")
            head_frac, tail_frac = self.fractions(heads, tails)
            return round(head_frac * 100, 2), round(tail_frac * 100, 2)

    class Analytics(Calculations):
        def __init__(self, data: list) -> None:
            super().__init__(data)
            logging.debug(f"Initializing Analytics with {len(data)} rows")

        def predict_random(self, n: int) -> list:
            logging.debug("Predicting random observations")
            result = []
            for _ in range(n):
                head = randint(0, 1)
                result.append([head, 1 - head])
            return result

        def predict_last(self) -> list:
            logging.debug("Returning the last observation")
            return self.data[-1]

        def save_file(self, data: str, filename: str, extension: str) -> None:
            logging.debug(f"Saving the report to {filename}.{extension}")
            with open(f"{filename}.{extension}", "w") as f:
                f.write(data)