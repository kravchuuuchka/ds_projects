import sys


def letter_starter(email):
    text = (
        "welcome to our team! "
        "We are sure that it will be a pleasure to work with you. "
        "That’s a precondition for the professionals that our company hires."
    )
    with open("../../datasets/employees.tsv", "r") as f:
        next(f)
        for line in f:
            name, _, emp_email = line.strip().split("\t")
            if emp_email == email:
                print(f"Dear {name}, {text}")
                return


if __name__ == '__main__':
    if len(sys.argv) == 2:
        letter_starter(sys.argv[1].lower())