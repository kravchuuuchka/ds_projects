#!/usr/bin/env python3
import timeit
import sys
from functools import reduce


def sum_of_squares_loop(n):
    total = 0
    for i in range(1, n + 1):
        total = total + i ** 2
    return total


def sum_of_squares_reduce(n):
    return reduce(lambda acc, i: acc + i ** 2, range(1, n + 1), 0)


def main():
    functions = {
        'loop': sum_of_squares_loop,
        'reduce': sum_of_squares_reduce,
    }

    if len(sys.argv) != 4:
        raise ValueError(f'Usage: {sys.argv[0]} <function_name> <number_of_calls> <n>')

    name = sys.argv[1]
    if name not in functions:
        raise ValueError(f'Unknown function: {name}. Available: {", ".join(functions)}')

    number_calls = int(sys.argv[2])
    if number_calls <= 0:
        raise ValueError(f'Number of calls must be a positive integer, got: {number_calls}')

    upper_limit = int(sys.argv[3])
    if upper_limit <= 0:
        raise ValueError(f'N must be a positive integer, got: {upper_limit}')

    fn = functions[name]
    result = timeit.timeit(lambda: fn(upper_limit), number=number_calls)
    print(result)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)