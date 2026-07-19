#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file1.csv> [file2.csv ...]"
    echo "Example: $0 2020-04-11.csv 2020-04-12.csv"
    exit 1
fi

head -1 "$1" > hh_positions.csv

for f in "$@"; do
    tail -n +2 "$f"
done >> hh_positions.csv

echo "Done. Results saved to hh_positions.csv"
