#!/usr/bin/env python3
import sys
import resource


def read_lines_generator(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line


def main():
    if len(sys.argv) != 2:
        raise ValueError(f'Usage: {sys.argv[0]} <file_path>')

    filepath = sys.argv[1]

    for _ in read_lines_generator(filepath):
        pass

    usage = resource.getrusage(resource.RUSAGE_SELF)
    peak_memory_gb = usage.ru_maxrss / (1024 ** 2)
    user_system_time = usage.ru_utime + usage.ru_stime

    print(f'Peak Memory Usage = {peak_memory_gb:.3f} GB')
    print(f'User Mode Time + System Mode Time = {user_system_time:.2f}s')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)