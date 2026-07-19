#!/usr/bin/env python3
import timeit
import random
from collections import Counter


def build_dict(numbers):
    result = {}
    for number in numbers:
        if number in result:
            result[number] += 1
        else:
            result[number] = 1
    print(result)
    return result


def build_dict_counter(numbers):
    result = Counter(numbers)
    return result


def top_ten(numbers):
    counts = build_dict(numbers)
    sorted_items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    print(dict(sorted_items[:10]))
    return dict(sorted_items[:10])


def top_ten_counter(numbers):
    print(dict(Counter(numbers).most_common(10)))
    return dict(Counter(numbers).most_common(10))


def main():
    numbers = [random.randint(0, 100) for _ in range(1_000_000)]

    number_calls = 1

    time_dict = timeit.timeit(lambda: build_dict(numbers), number=number_calls)
    time_counter = timeit.timeit(lambda: build_dict_counter(numbers), number=number_calls)
    time_top = timeit.timeit(lambda: top_ten(numbers), number=number_calls)
    time_top_counter = timeit.timeit(lambda: top_ten_counter(numbers), number=number_calls)

    print(f'my function: {time_dict}')
    print(f'Counter: {time_counter}')
    print(f'my top: {time_top}')
    print(f"Counter's top: {time_top_counter}")


if __name__ == '__main__':
    main()