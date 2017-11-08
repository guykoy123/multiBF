import Queue
import itertools
import string

# Globals:
CHUNK_SIZE = 100
RANGE_LENGTH = 100000
PASSWORD_LENGTH = 6

password_generator = itertools.product(string.ascii_lowercase, repeat=PASSWORD_LENGTH)
password_generator_empty = False
password_queue = Queue.Queue()


def _generate_range():
    """
    _generate_range _generate_range() -> tuple

    Generate range of passwords of certain length.
    """

    global PASSWORD_LENGTH
    global password_generator
    global password_generator_empty

    try:

        # start position
        start = password_generator.next()

    except StopIteration:

        password_generator_empty = True

    else:

        for i in range(RANGE_LENGTH):

            try:

                # stop position
                # update every round in case of exception
                stop = password_generator.next()

            except StopIteration:

                password_generator_empty = True

        else:

            start = ''.join(start)
            stop = ''.join(stop)

            return start, stop


def generate_chunk():
    """
    generate_chunk generate_chunk()

    Generate chunk of password ranges.
    """

    global CHUNK_SIZE
    global password_queue
    global password_generator_empty

    count = 0

    while count < CHUNK_SIZE and not password_generator_empty:

        new_range = _generate_range()

        if new_range:
            password_queue.put(new_range)

        count += 1
