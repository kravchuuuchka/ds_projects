import sys


def names_extractor(filepath):
    with open(filepath, "r") as f:
        with open("../../datasets/employees.tsv", "w") as out:
            out.write("Name\tSurname\tEmail\n")
            for line in f:
                email = line.strip()
                if email:
                    name, surname = email.split("@")[0].split(".")
                    out.write(f"{name.capitalize()}\t{surname.capitalize()}\t{email}\n")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        names_extractor(f"../../datasets/{sys.argv[1]}")