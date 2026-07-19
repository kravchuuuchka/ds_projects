#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path to hh_positions.csv>"
    echo "Example: $0 ../ex03/hh_positions.csv"
    exit 1
fi

HEADER=$(head -1 "$1")

tail -n +2 "$1" | while IFS= read -r line; do
    date=$(echo "$line" | cut -d',' -f2 | tr -d '"' | cut -dT -f1)

    outfile="${date}.csv"

    if [ ! -f "$outfile" ]; then
        echo "$HEADER" > "$outfile"
    fi

    echo "$line" >> "$outfile"
done

echo "Done. Partition files created."
