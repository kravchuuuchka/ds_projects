import sys


def shift_char(char, shift):
    if char.islower():
        return chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
    elif char.isupper():
        return chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
    return char


def caesar(mode, text, shift):
    for char in text:
        if char.isalpha() and not char.isascii():
            raise ValueError("The script does not support your language yet.")

    if mode == 'encode':
        return ''.join(shift_char(c, shift) for c in text)
    elif mode == 'decode':
        return ''.join(shift_char(c, -shift) for c in text)
    else:
        raise ValueError(f"Unknown mode: {mode}")


if __name__ == '__main__':
    try:
        if len(sys.argv) != 4:
            raise ValueError("Wrong number of arguments.")
        if not sys.argv[3].isdigit():
            raise ValueError("Shift must be a number.")

        print(caesar(sys.argv[1], sys.argv[2], int(sys.argv[3])))
    except ValueError as e:
        print(e)