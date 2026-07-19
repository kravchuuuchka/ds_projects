#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path to hh_positions.csv>"
    echo "Example: $0 ../ex03/hh_positions.csv"
    exit 1
fi

echo '"name","count"' > hh_uniq_positions.csv

tail -n +2 "$1" \
    | cut -d',' -f3 \
    | sort \
    | uniq -c \
    | sort -rn \
    | awk '{printf "%s,%s\n", $2, $1}' \
    >> hh_uniq_positions.csv

echo "Done. Results saved to hh_uniq_positions.csv"
