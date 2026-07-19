#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path to hh_sorted.csv>"
    echo "Example: $0 ../ex02/hh_sorted.csv"
    exit 1
fi

head -1 "$1" > hh_positions.csv

tail -n +2 "$1" | while IFS= read -r line; do
    name=$(echo "$line" | awk '
    {
        field = 0
        in_quotes = 0
        result = ""
        for (i = 1; i <= length($0); i++) {
            c = substr($0, i, 1)
            if (c == "\"") {
                in_quotes = !in_quotes
            } else if (c == "," && !in_quotes) {
                field++
                if (field == 3) { print result; exit }
                result = ""
            } else {
                result = result c
            }
        }
    }')

    result=$(echo "$name" | \
        tr '[:upper:]' '[:lower:]' | \
        grep -ow '\(junior\|middle\|senior\)' | \
        sed 's/./\u&/' | \
        tr '\n' '/' | \
        sed 's|/$||')

    [ -z "$result" ] && result="-"

    echo "$line" | awk -v rep="\"$result\"" '
    {
        field = 0
        in_quotes = 0
        out = ""
        cur = ""
        for (i = 1; i <= length($0); i++) {
            c = substr($0, i, 1)
            if (c == "\"") {
                in_quotes = !in_quotes
                cur = cur c
            } else if (c == "," && !in_quotes) {
                field++
                if (field == 3) {
                    out = out rep ","
                    cur = ""
                } else {
                    out = out cur ","
                    cur = ""
                }
            } else {
                cur = cur c
            }
        }
        out = out cur
        print out
    }'
done >> hh_positions.csv

echo "Done. Results saved to hh_positions.csv"
