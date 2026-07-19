import sys


def call_center(clients, recipients):
    return list(set(clients) - set(recipients))


def potential_clients(clients, participants):
    return list(set(participants) - set(clients))


def loyalty_program(clients, participants):
    return list(set(clients) - set(participants))


def marketing(task):
    clients = [
        'andrew@gmail.com',
        'jessica@gmail.com',
        'ted@mosby.com',
        'john@snow.is',
        'bill_gates@live.com',
        'mark@facebook.com',
        'elon@paypal.com',
        'jessica@gmail.com'
    ]
    participants = [
        'walter@heisenberg.com',
        'vasily@mail.ru',
        'pinkman@yo.org',
        'jessica@gmail.com',
        'elon@paypal.com',
        'pinkman@yo.org',
        'mr@robot.gov',
        'eleven@yahoo.com'
    ]
    recipients = [
        'andrew@gmail.com',
        'jessica@gmail.com',
        'john@snow.is'
    ]

    if task == 'call_center':
        print(call_center(clients, recipients))
    elif task == 'potential_clients':
        print(potential_clients(clients, participants))
    elif task == 'loyalty_program':
        print(loyalty_program(clients, participants))
    else:
        raise ValueError(f"Unknown task: {task}")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        try:
            marketing(sys.argv[1].lower())
        except ValueError as e:
            print(e)