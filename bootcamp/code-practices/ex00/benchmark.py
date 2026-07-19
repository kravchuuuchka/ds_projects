#!/usr/bin/env python3
import timeit


def filter_gmail_loop(emails):
    result = []
    for email in emails:
        if email.endswith('@gmail.com'):
            result.append(email)
    print(result)
    return result


def filter_gmail_comprehension(emails):
    result = [email for email in emails if email.endswith('@gmail.com')]
    print(result)
    return result


def main():
    emails = ['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com','anna@live.com', 'philipp@gmail.com']
    emails *= 5

    number_calls = 90

    time_loop = timeit.timeit(
        lambda: filter_gmail_loop(emails),
        number=number_calls
    )

    time_comprehension = timeit.timeit(
        lambda: filter_gmail_comprehension(emails),
        number=number_calls
    )

    if time_comprehension <= time_loop:
        winner = 'list comprehension'
    else:
        winner = 'loop'
    print(f'It is better to use a {winner}')
    print(f'{min(time_loop, time_comprehension)} vs {max(time_loop, time_comprehension)}')


if __name__ == '__main__':
    main()