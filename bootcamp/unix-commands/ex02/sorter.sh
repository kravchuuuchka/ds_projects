#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path to hh.csv>"
    echo "Example: $0 ../ex01/hh.csv"
    exit 1
fi

head -1 "$1" > hh_sorted.csv
tail -n +2 "$1" | sort -t',' -k2,2 -k1,1 >> hh_sorted.csv

echo "Done. Results saved to hh_sorted.csv"
