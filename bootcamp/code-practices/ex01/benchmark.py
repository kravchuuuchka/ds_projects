#!/usr/bin/env python3
import timeit


def filter_gmail_loop(emails):
    result = []
    for email in emails:
        if email.endswith('@gmail.com'):
            result.append(email)
    
    return result


def filter_gmail_comprehension(emails):
    return [email for email in emails if email.endswith('@gmail.com')]


def filter_gmail_map(emails):
    return list(map(lambda e: e if e.endswith('@gmail.com') else None, emails))


def main():
    emails = ['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com',
              'anna@live.com', 'philipp@gmail.com']
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

    time_list_map = timeit.timeit(
        lambda: filter_gmail_map(emails),
        number=number_calls
    )

    results = {
        'loop': time_loop,
        'list comprehension': time_comprehension,
        'map': time_list_map,
    }

    sorted_results = sorted(results.items(), key=lambda item: item[1])

    winner = sorted_results[0][0]
    print(f'It is better to use a {winner}')
    print(' vs '.join(str(t) for _, t in sorted_results))


if __name__ == '__main__':
    main()