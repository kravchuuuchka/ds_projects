#!/usr/bin/env python3
import timeit
import sys

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


def filter_gmail_filter(emails):
    return list(filter(lambda e: e.endswith('@gmail.com'), emails))


def main():
    emails = ['john@gmail.com', 'james@gmail.com', 'alice@yahoo.com',
              'anna@live.com', 'philipp@gmail.com'] * 5

    functions = {
        'loop': filter_gmail_loop,
        'list_comprehension': filter_gmail_comprehension,
        'map': filter_gmail_map,
        'filter': filter_gmail_filter,
    }

    if len(sys.argv) != 3:
        raise ValueError(f'Usage: {sys.argv[0]} <function_name> <number_of_calls>')

    name = sys.argv[1]
    if name not in functions:
        raise ValueError('Unknown function')
    
    number_calls = int(sys.argv[2])
    if number_calls <= 0:
        raise ValueError('Number of calls must be a positive integer')    

    fn = functions[name]
    result = timeit.timeit(lambda: fn(emails), number=number_calls)
    print(result)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)