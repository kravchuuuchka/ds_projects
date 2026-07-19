#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <job title>"
    echo "Example: $0 \"data scientist\""
    exit 1
fi

QUERY="$1"
ENCODED_QUERY=$(printf '%s' "$QUERY" | jq -sRr @uri)

curl -s \
    -H "Authorization: Bearer ${HH_TOKEN}" \
    -A "${HH_AGENT}" \
    "https://api.hh.ru/vacancies?text=${ENCODED_QUERY}&page=0&per_page=20" \
    | jq '.' > hh.json

echo "Done. Results saved to hh.json"
