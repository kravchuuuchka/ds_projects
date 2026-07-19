def parse_csv_line(line):
    fields = []
    current = ""
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(current)
            current = ""
        else:
            current += char

    fields.append(current)
    return fields


def read_and_write(input_file, output_file):
    with open(input_file, "r") as input_f:
        with open(output_file, "w") as output_f:
            for line in input_f:
                line = line.rstrip("\n")
                fields = parse_csv_line(line)
                output_f.write("\t".join(fields) + "\n")


if __name__ == "__main__":
    read_and_write(f"../../datasets/ds.csv", f"../../datasets/ds.tsv")