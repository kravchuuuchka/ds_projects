#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path to json file>"
    echo "Example: $0 ../ex00/hh.json"
    exit 1
fi

jq -rf filter.jq "$1" > hh.csv

echo "Done. Results saved to hh.csv"
