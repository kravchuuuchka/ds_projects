#!/usr/bin/env python3
import sys
import resource


def read_all_lines(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()


def main():
    if len(sys.argv) != 2:
        raise ValueError(f'Usage: {sys.argv[0]} <file_path>')

    filepath = sys.argv[1]
    lines = read_all_lines(filepath)

    for _ in lines:
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